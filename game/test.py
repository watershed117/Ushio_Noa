import os
import queue
import threading
import time
import logging
from typing import Any, Callable, Dict, Optional, List
from pydantic import validate_call, ValidationError
from colorama import Fore, Style, init
from datetime import datetime, timedelta
from itertools import count

# --------------------------
# 线程安全的ID生成器
# --------------------------
# 使用单调递增计数器 + 线程本地存储
from itertools import count
import threading

class IDGenerator:
    def __init__(self):
        self._local = threading.local()
    
    def __call__(self)->str:
        if not hasattr(self._local, 'counter'):
            self._local.counter = count()
        return f"T-{threading.get_ident()}-{next(self._local.counter)}"

gen = IDGenerator()

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
# 增强日志系统
# --------------------------
# 初始化colorama
init(autoreset=True)
class LogFilter(logging.Filter):
    """日志过滤器，清理空字段"""
    def filter(self, record):
        # 清理空字符串字段
        for field in ['event_id', 'func_name', 'func_args', 'func_kwargs']:
            value = getattr(record, field, "")
            if isinstance(value, (list, tuple, dict)) and not value:
                setattr(record, field, "")
            elif isinstance(value, str) and not value.strip():
                setattr(record, field, "")
        return True

class EnhancedColoredFormatter(logging.Formatter):
    """智能日志格式化器，自动隐藏空字段"""
    COLOR_MAP = {
        logging.DEBUG: Fore.CYAN + Style.DIM,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }
    
    def __init__(self,max_exc_len: int = 1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.empty_checker = LogFilter()
        self.max_exc_len = max_exc_len

    def format(self, record: logging.LogRecord) -> str:
        # 应用过滤器清理空字段
        self.empty_checker.filter(record)
        
        # 颜色配置
        time_color = Fore.LIGHTBLACK_EX
        name_color = Fore.WHITE
        level_color = self.COLOR_MAP.get(record.levelno, Fore.WHITE)
        event_id_color = Fore.BLUE
        func_color = Fore.YELLOW
        param_color = Fore.CYAN
        error_color = Fore.RED

        # 构建基础信息
        time_str = f"{time_color}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}"
        level_str = f"{level_color}{record.levelname}{Style.RESET_ALL}"
        name_str = f"{name_color}{record.name}{Style.RESET_ALL}"

        # 智能字段组装
        parts = []
        
        # 事件ID
        event_id = getattr(record, 'event_id', '')
        if event_id:
            parts.append(f"[EVENT {event_id_color}{event_id}{Style.RESET_ALL}]")

        # 函数信息
        func_name = getattr(record, 'func_name', '')
        func_args = getattr(record, 'func_args', ())
        func_kwargs = getattr(record, 'func_kwargs', {})

        if func_name:
            # 构建参数表示
            args_str = ""
            if func_args:
                args_str += f"{param_color}{func_args}{Style.RESET_ALL}"
            if func_kwargs:
                args_str += (", " if args_str else "") + f"{param_color}{func_kwargs}{Style.RESET_ALL}"
            
            func_str = f"{func_color}{func_name}{Style.RESET_ALL}"
            if args_str:
                func_str += f"({args_str})"
            parts.append(func_str)

        # 原始消息
        msg = record.getMessage().strip()
        if msg:
            # 处理多行消息
            if '\n' in msg and parts:
                msg = "\n  " + msg.replace('\n', '\n  ')
            parts.append(msg)

        # 组合日志行
        log_line = f"{time_str} | {level_str} | {name_str} | {' | '.join(parts)}"

        # 异常信息
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            log_line += f"\n{error_color}{exc_text}{Style.RESET_ALL}"[:self.max_exc_len]

        return log_line

def create_logger(name: str) -> logging.Logger:
    """创建优化后的日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    
    handler = logging.StreamHandler()
    handler.setFormatter(EnhancedColoredFormatter(
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    
    logger.addHandler(handler)
    logger.addFilter(LogFilter())
    return logger

# --------------------------
# 事件循环类（线程池版本）
# --------------------------
class EventLoopError(Exception):
    """事件循环异常基类"""
    pass

class MethodNotFoundError(EventLoopError):
    """方法不存在异常"""
    def __init__(self, method_name: str):
        super().__init__(f"Method '{method_name}' not found")
        self.method_name = method_name

class EventLoop:
    def __init__(self, num_workers: Optional[int] = None, validate_args: bool = True, logger:bool = True,result_ttl: int = 600,cleanup_interval: int = 600):
        self.event_results = {}
        self.event_queue = queue.Queue()
        
        self.logger = create_logger("EventLoop")
        if logger:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)

        self.validate_args = validate_args

        self.lock = threading.RLock()

        self.results_lock = threading.Lock()  # 专门保护event_results
        self.cleanup_lock = threading.Lock()   # 清理专用锁
        self.results_condition = threading.Condition(self.results_lock)
        self.cleanup_condition = threading.Condition(self.cleanup_lock)

        self.num_workers = num_workers or (os.cpu_count() or 1)
        
        self.workers = []
        self.running = False

        self.result_ttl = timedelta(seconds=result_ttl)
        self.last_cleanup = datetime.now()
        self.cleanup_interval = cleanup_interval  # 清理间隔(秒)
        
    def cleanup_worker(self):
        """定期清理过期结果的工作线程"""
        self.logger.info("清理线程已启动", extra={"func_name": "cleanup_worker"})
        while self.running:
            time.sleep(self.cleanup_interval)
            with self.cleanup_lock:
                self.logger.debug("开始清理", extra={"func_name": "EventLoop.cleanup_worker"})
                self._auto_cleanup()

    def _auto_cleanup(self):
        """根据TTL清理过期结果"""
        now = datetime.now()
        to_delete = []
        
        # 查找过期结果
        with self.results_lock:
            for eid, data in self.event_results.items():
                if now - data["create_time"] > self.result_ttl:
                    to_delete.append(eid)
        
        # 删除过期结果
        with self.results_lock:
            for eid in to_delete:
                del self.event_results[eid]
            
        self.last_cleanup = now
        if to_delete:  # 只有当实际清理了内容时才记录日志
            self.logger.info(f"已清理 {len(to_delete)} 条过期结果", 
                            extra={"func_name": "_auto_cleanup"})

    def start(self):
        """启动线程池"""
        cleanup_thread = threading.Thread(target=self.cleanup_worker, daemon=True)
        cleanup_thread.start()
        with self.lock:
            if self.running:
                return
            self.running = True
            for _ in range(self.num_workers):
                worker = threading.Thread(target=self.run_worker, daemon=True)
                worker.start()
                self.workers.append(worker)
            self.logger.info(
                "启动线程池",
                extra={"func_name": "EventLoop.start", "func_kwargs": {"worker_count": self.num_workers}}
            )

    def run_worker(self):
        """工作线程主逻辑"""
        while True:
            event_id, event = self.event_queue.get()

            if event == "stop":
                self.event_queue.task_done()
                break
            else:
                result = self.process_event(event)
                self._update_event_result(event_id, result)
                self.event_queue.task_done()

    def shutdown(self):
        """优雅停止线程池"""
        with self.lock:
            self.running = False

        for _ in range(self.num_workers):
            self.event_queue.put((gen(), "stop"))
        
        for worker in self.workers:
            worker.join()
        self.workers.clear()
        self.event_queue.join()
        self.logger.info("线程池已停止", extra={"func_name": "EventLoop.shutdown"})

    def call_function(self, func: Callable, *args, **kwargs) -> Any:
        """调用函数并处理异常及参数验证"""
        if not callable(func):
            raise TypeError(f"传入的对象 {func} 不可调用")
        if self.validate_args:
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
            except Exception as e:
                raise e
        else:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise e

    def process_event(self, event: Any) -> Any:
        """处理事件并返回结果或异常字典"""
        try:
            if isinstance(event, tuple):
                func, args, kwargs = event
                return self.call_function(func, *args, **kwargs)
            else:
                return self.call_function(event)
        except Exception as e:
            return {"error": e}

    def add_event(self, func: Callable, *args, **kwargs) -> str:
        """添加事件并返回ID"""
        event_id = gen()
        with self.results_lock:
            self.event_results[event_id] = {"status": "pending", "result": None,"create_time": datetime.now()}
        
        self.logger.info(
            "添加新任务",
            extra={
                "event_id": str(event_id),
                "func_name": func.__name__,
                "func_args": args,
                "func_kwargs": kwargs
            }
        )

        self.event_queue.put((event_id, (func, args, kwargs)))
        return event_id

    def get_event_result(self, event_id: str,timeout: Optional[float] = None) -> Dict[str, Any]:
        """获取结果，如果结果未就绪则等待"""
        with self.results_condition:
            start_time = time.monotonic()
            if event_id not in self.event_results:
                raise EventLoopError(f"Event {event_id} does not exist")

            while self.event_results[event_id]["status"] == "pending":
                remaining = timeout - (time.monotonic() - start_time) if timeout else None
                if remaining and remaining <= 0:
                    raise TimeoutError(f"等待结果超时 ({timeout}s)")
                self.results_condition.wait(remaining)
        return self.event_results.pop(event_id)
        
    def _update_event_result(self, event_id: str, result: Any):
        """更新事件结果并通知等待的线程"""
        with self.results_condition:
            if isinstance(result, dict) and "error" in result:
                error = result["error"]
                self.event_results[event_id].update({"status": "error", "result": error})
                self.logger.error(
                    "任务执行失败",
                    extra={
                        "event_id": str(event_id),
                        "func_name": "EventLoop._update_event_result"
                    },
                    exc_info=(type(error), error, error.__traceback__) if isinstance(error, Exception) else None
                )
            else:
                self.event_results[event_id].update({"status": "completed", "result": result})
                self.logger.info(
                    "任务执行完成",
                    extra={
                        "event_id": str(event_id),
                        "func_name": "EventLoop._update_event_result",
                        "task_result": str(result)
                    }
                )
            self.results_condition.notify_all()

if __name__ == "__main__":
    import time
    import threading
    # 配置全局日志
    root_logger = create_logger("Global")
    root_logger.setLevel(logging.INFO)

    # 禁用第三方库的日志
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").propagate = False

    class Test:        
        def test_method(self, arg1: int, arg2: int):
            """测试方法"""
            return arg1 + arg2

        def test_method2(self):
            """无参数测试方法"""
            return "success"
        
        def long_time_task(self):
            """耗时任务"""
            time.sleep(5)
            return None

    test_instance = Test()
    event_loop = EventLoop(num_workers=2, validate_args=False, logger=False,result_ttl=30, cleanup_interval=30)  # 使用线程池版本
    t=threading.Thread(target=event_loop.start)  # 启动线程池
    t.start()
    
    # 提交测试用例
    event_ids = []
    # event_ids.append(event_loop.add_event(test_instance.test_method, 1, 2))              # 正常调用
    # event_ids.append(event_loop.add_event(test_instance.test_method, arg1=3, arg2=4))    # 关键字参数调用
    # event_ids.append(event_loop.add_event(test_instance.test_method2))                   # 无参方法
    # event_ids.append(event_loop.add_event(test_instance.test_method, 1))                 # 参数不足
    # event_ids.append(event_loop.add_event(test_instance.test_method, "a", "b"))          # 错误参数类型
    # event_ids.append(event_loop.add_event(test_instance.long_time_task))                 # 耗时任务

    import requests
    import time
    start = time.monotonic()
    for i in range(10):
        event_ids.append(event_loop.add_event(requests.get, "https://www.example.com"))

    # for _ in range(100000):
    #     event_id = event_loop.add_event(lambda x: x, 42)
    #     event_ids.append(event_id)

    # 等待测试用例处理完成

    timeout=0
    error=0
    noexist=0
    for eid in event_ids[:]:
        try:
            result = event_loop.get_event_result(eid,5)
            if result["status"] == "error":
                root_logger.error(f"事件 {eid} 处理失败: {result['result']}")
                error+=1
            else:
                root_logger.debug(f"事件 {eid} 已处理，结果: {result['result']}")
                if result["result"].status_code != 200:
                    root_logger.error(f"事件 {eid} 处理失败: {result['result'].status_code}")
                    error+=1
            event_ids.remove(eid)  # 移除已处理的事件ID
        except TimeoutError:
            root_logger.error(f"事件 {eid} 处理超时")
            event_ids.remove(eid)  # 移除超时的事件ID
            timeout+=1
        except EventLoopError as e:
            root_logger.error(f"事件 {eid} 不存在或已被移除: {e}")
            event_ids.remove(eid)  # 从列表中移除无效的任务
            noexist+=1

    end = time.monotonic()
    root_logger.info(f"总耗时: {end - start:.4f} 秒")
    root_logger.info(f"超时: {timeout} 条, 不存在: {noexist} 条, 失败: {error} 条")

    # # 轮询等待事件处理完成
    # while event_ids:
    #     for eid in event_ids[:]:  # 使用 event_ids[:] 创建副本以避免修改迭代中的列表
    #         if eid in event_loop.event_results:
    #             status = event_loop.event_results[eid]["status"]
    #             if status == "completed":
    #                 result = event_loop.get_event_result(eid).get("result")
    #                 logger.info(f"事件 {eid} 已处理，结果: {result}")
    #                 event_ids.remove(eid)
    #             elif status == "error":
    #                 error = event_loop.get_event_result(eid).get("result")
    #                 logger.error(f"事件 {eid} 处理失败: {error}")
    #                 event_ids.remove(eid)
    #             else:
    #                 pass
    #         else:
    #             logger.error(f"事件 {eid} 不存在或已被移除")
    #             event_ids.remove(eid)  # 从列表中移除无效的任务
    #     time.sleep(1)  # 每隔 1 秒检查一次

    root_logger.info("所有事件处理完成")
    if not event_loop.event_results:
        root_logger.info("event_results已处理完成")
    else:
        root_logger.error(f"event_results存在{len(event_loop.event_results)}条未处理的结果")


    time.sleep(3)
    # 停止线程池
    event_loop.shutdown()