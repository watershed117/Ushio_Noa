import os
import queue
import threading
import time
import logging
from typing import Any, Callable, Dict, Optional, List
from colorama import Fore, Style, init
from datetime import datetime, timedelta
from itertools import count

init(autoreset=True)

class IDGenerator:
    def __init__(self):
        self._local = threading.local()
    
    def __call__(self) -> str:
        if not hasattr(self._local, 'counter'):
            self._local.counter = count()
        return f"T-{threading.get_ident()}-{next(self._local.counter)}"

gen = IDGenerator()

class InvalidArgumentsError(Exception):
    def __init__(self, func_name: str, messages: List[str]):
        super().__init__(f"参数校验失败于 {func_name}")
        self.detail = {
            "function": func_name,
            "errors": [msg for msg in messages if msg]
        }
    
    def __str__(self) -> str:
        return "\n".join(f"[{Fore.RED}✗{Style.RESET_ALL}] {err}" for err in self.detail["errors"])
    
class NoneBotFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datefmt = "%Y-%m-%d %H:%M:%S.%f"[:-3]

    def format(self, record: logging.LogRecord) -> str:
        # 基础信息
        time_str = self.formatTime(record, self.datefmt)
        level_str = f"{record.levelname:8}"
        name_str = record.name
        
        # 构建消息主体
        message_parts = []
        
        # 添加事件ID和函数名
        if hasattr(record, 'event_id'):
            task_id = record.event_id # type: ignore
            message_parts.append(f"[{task_id}]")
        if hasattr(record, 'func_name'):
            func_name = record.func_name # type: ignore
            message_parts.append(f"{func_name}()")
        
        # 原始消息内容
        base_message = record.getMessage()
        
        # DEBUG级别添加参数详情
        if record.levelno == logging.DEBUG:
            arg_details = []
            if hasattr(record, 'func_args'):
                arg_details.append(f"args={getattr(record, 'func_args')}")
            if hasattr(record, 'func_kwargs'):
                arg_details.append(f"kwargs={getattr(record, 'func_kwargs')}")
            if hasattr(record, 'result'):
                arg_details.append(f"result={getattr(record, 'result')}")  
            if arg_details:
                base_message += " | " + ", ".join(arg_details)
        
        message_parts.append(base_message)
        
        # 组合完整消息
        full_message = " ".join(message_parts)
        
        # 异常信息处理
        exc_info = ""
        if record.exc_info:
            exc_info = "\n" + self.formatException(record.exc_info)
            exc_info = exc_info.replace("\n", "\n  | ")

        return f"{time_str} | {level_str} | {name_str} | {full_message}{exc_info}"
    
class Colored_NoneBotFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datefmt = "%Y-%m-%d %H:%M:%S.%f"[:-3]

    def format(self, record: logging.LogRecord) -> str:
        # 基础信息
        time_str = self.formatTime(record, self.datefmt)
        level_color = self.LEVEL_COLORS.get(record.levelno, "")
        level_str = f"{level_color}{record.levelname:8}{Style.RESET_ALL}"
        name_str = f"{Fore.LIGHTBLACK_EX}{record.name}{Style.RESET_ALL}"
        
        # 构建消息主体
        message_parts = []
        
        # 添加事件ID和函数名（与INFO级别相同）
        if hasattr(record, 'event_id'):
            task_id = record.event_id # type: ignore
            message_parts.append(f"[{Fore.BLUE}{task_id}{Style.RESET_ALL}]")
        if hasattr(record, 'func_name'):
            func_name = record.func_name # type: ignore
            message_parts.append(f"{Fore.YELLOW}{func_name}(){Style.RESET_ALL}")
        
        # 原始消息内容
        base_message = record.getMessage()
        
        # DEBUG级别添加参数详情（保持高亮）
        if record.levelno == logging.DEBUG:
            arg_details = []
            if hasattr(record, 'func_args'):
                arg_details.append(f"args={Fore.CYAN}{getattr(record, 'func_args')}{Style.RESET_ALL}")
            if hasattr(record, 'func_kwargs'):
                arg_details.append(f"kwargs={Fore.CYAN}{getattr(record, 'func_kwargs')}{Style.RESET_ALL}")
            if hasattr(record, 'result'):
                arg_details.append(f"result={Fore.GREEN}{getattr(record, 'result')}{Style.RESET_ALL}")  
            if arg_details:
                base_message += f" {Fore.LIGHTBLACK_EX}|{Style.RESET_ALL} " + f"{Fore.LIGHTBLACK_EX}, {Style.RESET_ALL}".join(arg_details)
        
        message_parts.append(base_message)
        
        # 错误级别特殊处理（与INFO级别相同）
        if record.levelno >= logging.ERROR:
            if "任务失败" in base_message:
                parts = base_message.split("任务失败", 1)
                if len(parts) > 1:
                    message_parts[-1] = (
                        f"{parts[0]}{Fore.RED}任务失败{Style.RESET_ALL}"
                        f"{Fore.RED}{parts[1]}{Style.RESET_ALL}"
                    )
            else:
                message_parts[-1] = f"{Fore.RED}{base_message}{Style.RESET_ALL}"
        
        # 组合完整消息
        full_message = " ".join(message_parts)
        
        # 异常信息处理（与INFO级别相同）
        exc_info = ""
        if record.exc_info:
            # 生成原始异常信息
            raw_exc = self.formatException(record.exc_info)
            
            # 关键修改点：分三步处理
            # 1. 给每行添加红色竖线前缀
            exc_lines = [f"{Fore.RED}  | {line}{Style.RESET_ALL}" 
                        for line in raw_exc.split('\n')]
            
            # 2. 包裹整个Traceback为红色
            red_exc = f"{Fore.RED}Traceback (most recent call last):{Style.RESET_ALL}\n" + \
                     '\n'.join(exc_lines[1:])  # 去掉原第一行
            
            # 3. 组合最终异常信息
            exc_info = f"\n{red_exc}"

        return f"{time_str} | {level_str} | {name_str} | {full_message}{exc_info}"
    
def setup_logger(name: str, level: int = logging.INFO,colored: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        if colored:
            handler.setFormatter(Colored_NoneBotFormatter())
        else:
            handler.setFormatter(NoneBotFormatter())
        logger.addHandler(handler)
    
    logger.propagate = False
    return logger

class EventLoopError(Exception):
    pass

class MethodNotFoundError(EventLoopError):
    def __init__(self, method_name: str):
        super().__init__(f"Method '{method_name}' not found")
        self.method_name = method_name

class EventLoop:
    def __init__(
        self,
        num_workers: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        log_level: int = logging.INFO,
        colored: bool = True,
        result_ttl: int = 600,
        cleanup_interval: int = 600
    ):
        self.event_results = {}
        self.event_queue = queue.Queue()
        self.logger = logger or setup_logger("EventLoop",colored=colored)
        self.logger.setLevel(log_level)
        self.lock = threading.RLock()
        self.results_lock = threading.Lock()
        self.cleanup_lock = threading.Lock()
        self.results_condition = threading.Condition(self.results_lock)
        self.num_workers = num_workers or (os.cpu_count() or 1)
        self.workers = []
        self.running = False
        self.result_ttl = timedelta(seconds=result_ttl)
        self.last_cleanup = datetime.now()
        self.cleanup_interval = cleanup_interval
        
    def cleanup_worker(self):
        self.logger.info("清理线程启动")
        while self.running:
            time.sleep(self.cleanup_interval)
            with self.cleanup_lock:
                self._auto_cleanup()

    def _auto_cleanup(self):
        now = datetime.now()
        to_delete = []
        
        with self.results_lock:
            for eid, data in self.event_results.items():
                if now - data["create_time"] > self.result_ttl:
                    to_delete.append(eid)
            
            for eid in to_delete:
                del self.event_results[eid]
        
        self.last_cleanup = now
        if to_delete:
            self.logger.info(f"清理{len(to_delete)}个超时结果")

    def start(self):
        with self.lock:
            if self.running:
                return
                
            self.running = True
            threading.Thread(target=self.cleanup_worker, daemon=True).start()
            
            for _ in range(self.num_workers):
                worker = threading.Thread(target=self.run_worker, daemon=True)
                worker.start()
                self.workers.append(worker)
                
            self.logger.info(f"启动线程池，工作线程数量：{self.num_workers}")

    def run_worker(self):
        while True:
            event_id, event = self.event_queue.get()

            if event == "stop":
                self.event_queue.task_done()
                break
                
            try:
                result = self.process_event(event)
                self._update_event_result(event_id, result)
            except Exception as e:
                self._update_event_result(event_id, e)
            finally:
                self.event_queue.task_done()

    def shutdown(self):
        with self.lock:
            self.running = False

        for _ in range(self.num_workers):
            self.event_queue.put((gen(), "stop"))
        
        for worker in self.workers:
            worker.join()
            
        self.workers.clear()
        self.event_queue.join()
        self.logger.info("Thread pool stopped")

    def call_function(self, func: Callable, *args, **kwargs) -> Any:
        if not callable(func):
            raise TypeError(f"{func} is not callable")
        return func(*args, **kwargs)

    def process_event(self, event: Any) -> Any:
        if isinstance(event, tuple):
            func, args, kwargs = event
            return self.call_function(func, *args, **kwargs)
        return self.call_function(event)

    def add_event(self, func: Callable, *args, **kwargs) -> str:
        event_id = gen()
        
        with self.results_lock:
            self.event_results[event_id] = {
                "status": "pending",
                "result": None,
                "create_time": datetime.now(),
                "func_name": func.__name__
            }
            self.event_queue.put((event_id, (func, args, kwargs)))
            self.logger.info(
                "接收任务",
                extra={
                    "event_id": event_id,
                    "func_name": func.__name__,
                }
            )

            self.logger.debug(
                "参数详情",  # 消息更简洁
                extra={
                    "event_id": event_id,
                    "func_name": func.__name__,
                    "func_args": args,
                    "func_kwargs": kwargs
                }
            )
        return event_id

    def get_event_result(self, event_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        with self.results_condition:
            start_time = time.monotonic()
            
            if event_id not in self.event_results:
                raise EventLoopError(f"Event {event_id} does not exist")

            while self.event_results[event_id]["status"] == "pending":
                remaining = timeout - (time.monotonic() - start_time) if timeout else None
                if remaining and remaining <= 0:
                    raise TimeoutError(f"Timeout after {timeout}s")
                self.results_condition.wait(remaining)
                
        return self.event_results.pop(event_id)
    
    def polling_result(self,eid:str,sleep_func:Callable[[float],None]=time.sleep,timeout:float=0.1)->Dict[str,Any]:
        """
        轮询事件结果
        """
        while True:
            if self.event_results[eid]["status"] == "pending":
                sleep_func(timeout)
            else:
                return self.event_results.pop(eid)

    def _update_event_result(self, event_id: str, result: Any):
        with self.results_condition:
            if event_id not in self.event_results:
                return
                
            data = self.event_results[event_id]
            func_name = data.get("func_name", "unknown")
            
            if isinstance(result, Exception):
                self.event_results[event_id].update({
                    "status": "error",
                    "result": result,
                    "processed_time": datetime.now()
                })
                
                self.logger.error(
                    "任务失败 - %s",  # 更简洁的格式
                    str(result),
                    extra={
                        "event_id": event_id,
                        "func_name": func_name,
                        "error_type": type(result).__name__
                    }
                )
                
                self.logger.debug(
                    "错误详情",  # 统一的消息格式
                    extra={"event_id": event_id},
                    exc_info=result
                )
            else:
                self.event_results[event_id].update({
                    "status": "completed",
                    "result": result,
                    "processed_time": datetime.now()
                })
                self.logger.info(
                    "任务完成",
                    extra={
                        "event_id": event_id,
                        "func_name": func_name
                    }
                )
                self.logger.debug(
                    "结果详情",  # 统一的消息格式
                    extra={
                        "event_id": event_id,
                        "func_name": func_name,
                        "result": result
                    }
                )
            
            self.results_condition.notify_all()

if __name__ == "__main__":
    logger = setup_logger("Test")
    logger.setLevel(logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    
    def test_task(n: int):
        time.sleep(0.5)
        if n % 5 == 0:
            raise ValueError(f"Bad number {n}")
        return n * 2
    
    loop = EventLoop(num_workers=4, log_level=logging.DEBUG,colored=True, result_ttl=30, cleanup_interval=30)
    loop.start()
    
    tasks = [loop.add_event(test_task, i) for i in range(1, 11)]
    
    # for task_id in tasks:
    #     try:
    #         result = loop.get_event_result(task_id, timeout=3)
    #         if result["status"] == "completed":
    #             pass  # 测试结果处理
    #     except TimeoutError:
    #         logger.warning(f"Task {task_id} timeout")
    #     except EventLoopError as e:
    #         logger.error(str(e))
    time.sleep(60)
    loop.shutdown()