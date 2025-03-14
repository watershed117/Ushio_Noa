from __future__ import annotations
import selectors
import uuid
import heapq
from time import monotonic
from collections import deque
from types import GeneratorType, TracebackType
from pydantic import validate_call, ConfigDict, ValidationError
from typing import Dict, Any, Callable, Union, List, Optional, Generator, Type, TypeVar, cast
import logging
from colorama import Fore, Style, init
import traceback
import sys

# --------------------------
# 异常体系
# --------------------------
class InvalidArgumentsError(Exception):
    """参数校验失败异常（支持结构化错误）"""
    def __init__(self, func_name: str, messages: List[str]):
        super().__init__(f"参数校验失败于 {func_name}")
        self.detail = {
            "function": func_name,
            "errors": [msg for msg in messages if msg]
        }
    
    def __str__(self) -> str:
        return "\n".join(
            f"[{Fore.RED}✗{Style.RESET_ALL}] {err}" 
            for err in self.detail["errors"]
        )

# --------------------------
# 日志系统
# --------------------------
init(autoreset=True)
class EnhancedColoredFormatter(logging.Formatter):
    """支持多字段彩色输出的日志格式化器（修复字段冲突）"""
    COLOR_MAP = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # 基础字段颜色
        time_color = Fore.LIGHTBLACK_EX
        name_color = Fore.WHITE
        level_color = self.COLOR_MAP.get(record.levelno, Fore.WHITE)
        
        # 特殊字段颜色
        event_id_color = Fore.BLUE
        func_color = Fore.YELLOW
        param_color = Fore.CYAN
        error_color = Fore.RED
        
        # 构建基础信息
        time_str = f"{time_color}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}"
        level_str = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        name_str = f"{name_color}{record.name}{Style.RESET_ALL}"
        
        # 提取扩展字段（使用非冲突字段名）
        event_id = f"{event_id_color}{getattr(record, 'event_id', '')}{Style.RESET_ALL}"
        func_name = f"{func_color}{getattr(record, 'func_name', '')}{Style.RESET_ALL}"
        # 修改点：使用func_args/func_kwargs避免冲突
        func_args = f"{param_color}{getattr(record, 'func_args', '')}{Style.RESET_ALL}"
        func_kwargs = f"{param_color}{getattr(record, 'func_kwargs', '')}{Style.RESET_ALL}"
        
        # 构建消息主体
        msg_parts = []
        if event_id.strip():
            msg_parts.append(f"[EVENT {event_id}]")
        if func_name.strip():
            msg_parts.append(f"Function: {func_name}")
        if func_args.strip() and func_args != "()":
            msg_parts.append(f"Args: {func_args}")
        if func_kwargs.strip() and func_kwargs != "{}":
            msg_parts.append(f"Kwargs: {func_kwargs}")
        
        # 添加原始消息
        msg = record.getMessage()
        if msg:
            msg_parts.append(f"Message: {msg}")
        
        # 组合基础信息
        log_line = f"{time_str} | {level_str} | {name_str} | {' | '.join(msg_parts)}"
        
        # 添加异常信息
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            log_line += f"\n{error_color}{exc_text}{Style.RESET_ALL}"
        
        return log_line

def create_logger(name: str) -> logging.Logger:
    """创建带彩色格式的logger实例"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    
    handler = logging.StreamHandler()
    handler.setFormatter(EnhancedColoredFormatter(
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    
    logger.addHandler(handler)
    return logger

# Type for Future
T = TypeVar('T')

# --------------------------
# 核心事件循环（带增强日志）
# --------------------------
class AsyncEventLoop:
    class Future:
        __slots__ = ('_state', '_result', '_exception', '_callbacks')
        
        def __init__(self) -> None:
            self._state: str = 'PENDING'
            self._result: Any = None
            self._exception: Optional[BaseException] = None
            self._callbacks: List[Callable[[], None]] = []
        
        def __str__(self) -> str:
            """改进 Future 的字符串表示，显示其状态和结果"""
            if self._state == 'PENDING':
                return f"<Future: PENDING>"
            elif self._state == 'ERROR':
                return f"<Future: ERROR {self._exception}>"
            else:
                return f"<Future: FINISHED {self._result}>"

        def _trigger_callbacks(self) -> None:
            for cb in self._callbacks:
                try:
                    cb()
                except Exception as e:
                    logging.error(f"回调异常: {e!r}")

        def add_done_callback(self, fn: Callable[[], None]) -> None:
            if self._state != 'PENDING':
                fn()
            else:
                self._callbacks.append(fn)

        def set_result(self, result: Any) -> None:
            if self._state != 'PENDING':
                raise RuntimeError("Future状态不可变")
            self._state = 'FINISHED'
            self._result = result
            self._trigger_callbacks()

        def set_exception(self, exc: BaseException) -> None:
            if not isinstance(exc, BaseException):
                raise TypeError("异常必须继承自BaseException")
            if self._state != 'PENDING':
                raise RuntimeError("Future状态不可变")
            self._state = 'ERROR'
            if not exc.__traceback__:
                exc.__traceback__ = self._capture_traceback()
            self._exception = exc
            self._trigger_callbacks()

        def _capture_traceback(self) -> TracebackType:
            frame = sys._getframe(2)
            tb = TracebackType(None, frame, frame.f_lasti, frame.f_lineno)
            while frame.f_back:
                frame = frame.f_back
                tb = TracebackType(tb, frame, frame.f_lasti, frame.f_lineno)
            return tb

        @property
        def done(self) -> bool:
            return self._state in ('FINISHED', 'ERROR')
            
        @property
        def result(self) -> Any:
            if self._state == 'PENDING':
                raise RuntimeError("Future还未完成")
            if self._state == 'ERROR' and self._exception is not None:
                raise self._exception
            return self._result

    def __init__(self) -> None:
        self._selector = selectors.DefaultSelector()
        self._ready: deque = deque()
        self._scheduled: List[tuple] = []
        self.event_results: Dict[uuid.UUID, Dict[str, Any]] = {}
        self.logger: logging.Logger = create_logger("AsyncEventLoop")
        self._stopping: bool = False


    def _update_result(self, event_id: Optional[uuid.UUID], result: Any) -> None:
        if event_id is None:
            return

        # 修复：从Future中提取实际结果
        if isinstance(result, self.Future):
            try:
                # 如果Future已完成，提取实际结果
                if result.done:
                    actual_result = result.result
                    self.event_results[event_id] = {"status": "completed", "result": actual_result}
                    self.logger.info(
                        "任务执行完成",
                        extra={
                            "event_id": str(event_id),
                            "task_result": str(actual_result)
                        }
                    )
                else:
                    # 如果Future尚未完成，保持pending状态
                    self.event_results[event_id] = {"status": "pending", "result": None}
            except Exception as e:
                # 如果Future抛出异常
                self.event_results[event_id] = {"status": "error", "result": e}
                self.logger.error(
                    "任务执行失败",
                    extra={"event_id": str(event_id)},
                    exc_info=(type(e), e, e.__traceback__)
                )
        elif isinstance(result, Exception):
            self.event_results[event_id] = {"status": "error", "result": result}
            self.logger.error(
                "任务执行失败",
                extra={"event_id": str(event_id)},
                exc_info=(type(result), result, result.__traceback__)
            )
        else:
            self.event_results[event_id] = {"status": "completed", "result": result}
            self.logger.info(
                "任务执行完成",
                extra={
                    "event_id": str(event_id),
                    "task_result": str(result)
                }
            )

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def add_event(self, 
                func: Union[Callable[..., Any], GeneratorType],
                *args: Any, **kwargs: Any) -> uuid.UUID:
        event_id = uuid.uuid4()
        self.event_results[event_id] = {"status": "pending", "result": None}
        
        try:
            func_name = getattr(func, "__name__", str(func))
            # 只使用func_args/func_kwargs字段名，删除冲突的第二个日志调用
            self.logger.info(
                "添加新任务",
                extra={
                    "event_id": str(event_id),
                    "func_name": func_name,
                    "func_args": args,      
                    "func_kwargs": kwargs   
                }
            )
            
            if isinstance(func, GeneratorType):
                coro = self._run_async(event_id, func)
                self._ready.append((event_id, coro))
            else:
                future = self.asyncify(func)(*args, **kwargs)
                if not future.done:
                    def future_wrapper():
                        yield future
                        return future.result
                    self._ready.append((event_id, future_wrapper()))
                else:
                    try:
                        result = future.result
                        self._update_result(event_id, result)
                    except Exception as e:
                        self._update_result(event_id, e)
        except Exception as e:
            self._update_result(event_id, e)
        
        return event_id

    def _run_async(self, event_id: uuid.UUID, coro: GeneratorType) -> Generator[Any, None, Any]:
        self.logger.debug(
            "开始执行协程",
            extra={"event_id": str(event_id)}
        )
        
        try:
            result = None
            while True:
                try:
                    future = coro.send(result)
                    result = None
                    self.logger.debug(
                        "协程产生Future",
                        extra={"event_id": str(event_id)}
                    )
                    
                    if isinstance(future, self.Future):
                        future.add_done_callback(
                            lambda _=None: self._ready.append((event_id, coro))
                        )
                        yield future
                    else:
                        yield future
                except StopIteration as e:
                    self.logger.debug(
                        "协程执行完成",
                        extra={"event_id": str(event_id)}
                    )
                    return e.value
        except Exception as e:
            self.logger.error(
                "协程执行异常",
                extra={"event_id": str(event_id)},
                exc_info=True
            )
            raise

    def asyncify(self, func: Callable[..., Any]) -> Callable[..., 'AsyncEventLoop.Future']:
        def wrapper(*args: Any, **kwargs: Any) -> 'AsyncEventLoop.Future':
            future = self.Future()
            try:
                result = self.call_function(func, *args, **kwargs)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            return future
        return wrapper

    def call_function(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        try:
            validated_func = validate_call(func)
            return validated_func(*args, **kwargs)
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                loc = error.get("loc", ())
                param_name = loc[-1] if loc else "未知参数"
                msg = f"参数 '{param_name}': {error['msg']}"
                error_messages.append(msg)
            raise InvalidArgumentsError(func.__name__, error_messages)

    def run(self, stop_when_idle: bool = False) -> None:
        try:
            while not self._stopping:
                # 处理就绪任务
                while self._ready:
                    event_id, coro = self._ready.popleft()
                    try:
                        next_yield = next(coro)
                        if isinstance(next_yield, self.Future):
                            next_yield.add_done_callback(
                                lambda _=None: self._ready.append((event_id, coro)))
                    except StopIteration as e:
                        self._update_result(event_id, e.value)
                    except Exception as e:
                        self._update_result(event_id, e)

                # 处理定时任务
                now = monotonic()
                while self._scheduled and self._scheduled[0][0] <= now:
                    deadline, callback = heapq.heappop(self._scheduled)
                    self.logger.debug(
                        "执行定时任务",
                        extra={"deadline": deadline, "func_name": callback.__name__}
                    )
                    self._ready.append((None, callback()))

                # 计算等待时间
                timeout = None
                if self._scheduled:
                    next_deadline = self._scheduled[0][0]
                    timeout = max(0, next_deadline - monotonic())

                # IO事件处理
                if timeout is not None or self._selector.get_map():
                    try:
                        events = self._selector.select(timeout)
                        for key, _ in events:
                            callback_obj = key.data
                            if isinstance(callback_obj, self.Future):
                                callback_obj.set_result(None)
                            self._selector.unregister(key.fileobj)
                    except Exception as e:
                        self.logger.error("IO事件处理异常", exc_info=True)
                elif not (self._ready or self._scheduled):
                    if stop_when_idle:
                        break
                    import time
                    time.sleep(0.01)
        finally:
            self._selector.close()

    def get_event_result(self, event_id: uuid.UUID) -> Dict[str, Any]:
        return self.event_results.get(event_id, {"status": "invalid", "result": None})

    def register_io(self, fileobj: Any, events: int, future: 'AsyncEventLoop.Future') -> None:
        self.logger.debug(
            "注册IO监听",
            extra={"fileobj": str(fileobj), "events": events}
        )
        try:
            if fileobj in [key.fileobj for key in self._selector.get_map().values()]:
                self._selector.unregister(fileobj)
            self._selector.register(fileobj, events, future)
        except Exception as e:
            self.logger.error("IO注册失败", exc_info=True)

    def schedule(self, delay: float, func: Callable[[], Generator]) -> None:
        if not isinstance(delay, (int, float)):
            raise TypeError(f"延迟时间应为数字，实际类型: {type(delay)}")
        deadline = monotonic() + delay
        heapq.heappush(self._scheduled, (deadline, func))
        self.logger.debug(
            "添加定时任务",
            extra={"delay": delay, "deadline": deadline}
        )

    def stop(self) -> None:
        self.logger.info("事件循环停止")
        self._stopping = True

# --------------------------
# 测试代码
# --------------------------
if __name__ == "__main__":
    import threading
    import time
    import requests
    import urllib3
    import socket
    from urllib3.util import parse_url

    loop = AsyncEventLoop()

    # 启动事件循环线程
    t = threading.Thread(target=loop.run, args=(True,))
    t.start()

    def async_http_get(url: str) -> Generator[Any, None, str]:
        # 使用底层socket实现非阻塞请求
        parsed = parse_url(url)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((parsed.host, parsed.port or 80))
        
        # 发送HTTP请求
        request = f"GET {parsed.path or '/'} HTTP/1.1\r\nHost: {parsed.host}\r\nConnection: close\r\n\r\n"
        sock.send(request.encode())
        
        # 交出socket控制权
        response = yield sock
        
        # 读取响应
        data = []
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data.append(chunk)
            except BlockingIOError:
                yield sock  # 继续等待数据
        
        sock.close()
        return b''.join(data).decode()

    # 添加任务
    ids = []
    start = time.monotonic()
    for i in range(10):
        request_id = loop.add_event(async_http_get, "https://www.example.com")
        ids.append(request_id)
        print(f"Added request {request_id}")

    # 等待所有任务完成
    while True:
        all_done = True
        for request_id in ids:
            result = loop.get_event_result(request_id)
            if result["status"] == "pending":
                all_done = False
                break
        if all_done:
            break
        time.sleep(0.1)  # 避免忙等待

    # 打印结果
    for request_id in ids:
        result = loop.get_event_result(request_id)
        print(f"Request {request_id} result: {result}")

    end = time.monotonic()
    print(f"Total time: {end - start:.2f}s")

    # 停止事件循环
    loop.stop()
    t.join()