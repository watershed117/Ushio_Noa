import os
import queue
import threading
import time
import logging
from typing import Any, Callable, Dict, Optional, List, Union
from colorama import Fore, Style, init
from datetime import datetime, timedelta
from itertools import count

# Initialize colorama
init(autoreset=True)

# --------------------------
# ID Generator
# --------------------------
class IDGenerator:
    def __init__(self):
        self._local = threading.local()
    
    def __call__(self) -> str:
        if not hasattr(self._local, 'counter'):
            self._local.counter = count()
        return f"T-{threading.get_ident()}-{next(self._local.counter)}"

gen = IDGenerator()

# --------------------------
# Exception Classes
# --------------------------
class InvalidArgumentsError(Exception):
    """Invalid arguments exception with structured errors"""
    def __init__(self, func_name: str, messages: List[str]):
        super().__init__(f"Invalid arguments for {func_name}")
        self.detail = {
            "function": func_name,
            "errors": [msg for msg in messages if msg]
        }
    
    def __str__(self) -> str:
        return "\n".join(
            f"[{Fore.RED}✗{Style.RESET_ALL}] {err}" 
            for err in self.detail["errors"]
        )

class EventLoopError(Exception):
    """Base event loop exception"""
    pass

class MethodNotFoundError(EventLoopError):
    """Method not found exception"""
    def __init__(self, method_name: str):
        super().__init__(f"Method '{method_name}' not found")
        self.method_name = method_name

# --------------------------
# Logging Configuration
# --------------------------
LogLevelType = Union[int, str]

class LogDetailLevel:
    """Controls how much detail is shown at each log level"""
    DEBUG = {
        'show_time': True,
        'show_level': True,
        'show_name': True,
        'show_event_id': True,
        'show_func_info': True,
        'show_args': True,
        'show_kwargs': True,
        'show_message': True,
        'show_exception': True,
        'show_result': True
    }
    INFO = {
        'show_time': True,
        'show_level': True,
        'show_name': True,
        'show_event_id': True,
        'show_func_info': True,
        'show_args': False,
        'show_kwargs': False,
        'show_message': True,
        'show_exception': True,
        'show_result': False
    }
    WARNING = {
        'show_time': True,
        'show_level': True,
        'show_name': True,
        'show_event_id': True,
        'show_func_info': True,
        'show_args': False,
        'show_kwargs': False,
        'show_message': True,
        'show_exception': True,
        'show_result': False
    }
    ERROR = {
        'show_time': True,
        'show_level': True,
        'show_name': True,
        'show_event_id': True,
        'show_func_info': True,
        'show_args': True,
        'show_kwargs': True,
        'show_message': True,
        'show_exception': True,
        'show_result': False
    }
    CRITICAL = {
        'show_time': True,
        'show_level': True,
        'show_name': True,
        'show_event_id': True,
        'show_func_info': True,
        'show_args': True,
        'show_kwargs': True,
        'show_message': True,
        'show_exception': True,
        'show_result': False
    }

class LogFilter(logging.Filter):
    """Filters empty log fields"""
    def filter(self, record):
        for field in ['event_id', 'func_name', 'func_args', 'func_kwargs', 'task_result']:
            value = getattr(record, field, "")
            if isinstance(value, (list, tuple, dict)) and not value:
                setattr(record, field, "")
            elif isinstance(value, str) and not value.strip():
                setattr(record, field, "")
        return True

class BaseFormatter:
    """Base formatter with common logic"""
    def __init__(self, max_exc_len: int = 1000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.empty_checker = LogFilter()
        self.max_exc_len = max_exc_len
        self.detail_levels = LogDetailLevel()

    def get_detail_level(self, record):
        """Get detail configuration for current log level"""
        level = record.levelno
        if level == logging.DEBUG:
            return self.detail_levels.DEBUG
        elif level == logging.INFO:
            return self.detail_levels.INFO
        elif level == logging.WARNING:
            return self.detail_levels.WARNING
        elif level == logging.ERROR:
            return self.detail_levels.ERROR
        else:  # CRITICAL
            return self.detail_levels.CRITICAL

    def format(self, record: logging.LogRecord) -> str:
        self.empty_checker.filter(record)
        detail = self.get_detail_level(record)
        
        parts = []
        
        # Timestamp
        if detail['show_time']:
            parts.append(self.format_time(record))
        
        # Log level
        if detail['show_level']:
            parts.append(self.format_level(record))
        
        # Logger name
        if detail['show_name']:
            parts.append(self.format_name(record))
        
        # Event ID
        event_id = getattr(record, 'event_id', '')
        if detail['show_event_id'] and event_id:
            parts.append(self.format_event_id(record, event_id))
        
        # Function info
        func_name = getattr(record, 'func_name', '')
        if detail['show_func_info'] and func_name:
            parts.append(self.format_func_info(record, func_name, detail))
        
        # Message
        msg = record.getMessage().strip()
        if detail['show_message'] and msg:
            parts.append(self.format_message(record, msg))
        
        # Task result
        task_result = getattr(record, 'task_result', '')
        if detail['show_result'] and task_result:
            parts.append(self.format_result(record, task_result))
        
        # Combine parts
        log_line = ' | '.join(parts)
        
        # Exception info
        if record.exc_info and detail['show_exception']:
            exc_text = self.format_exception(record)
            log_line += f"\n{exc_text[:self.max_exc_len]}"
        
        return log_line
    
    # Methods to be implemented by subclasses
    def format_time(self, record):
        raise NotImplementedError
        
    def format_level(self, record):
        raise NotImplementedError
        
    def format_name(self, record):
        raise NotImplementedError
        
    def format_event_id(self, record, event_id):
        raise NotImplementedError
        
    def format_func_info(self, record, func_name, detail):
        raise NotImplementedError
        
    def format_message(self, record, msg):
        raise NotImplementedError
        
    def format_result(self, record, result):
        raise NotImplementedError
        
    def format_exception(self, record):
        raise NotImplementedError

class EnhancedPlainTextFormatter(BaseFormatter, logging.Formatter):
    """Plain text formatter without colors"""
    
    def format_time(self, record):
        return self.formatTime(record, self.datefmt)
    
    def format_level(self, record):
        return record.levelname
    
    def format_name(self, record):
        return record.name
    
    def format_event_id(self, record, event_id):
        return f"[EVENT {event_id}]"
    
    def format_func_info(self, record, func_name, detail):
        args_str = ""
        if detail['show_args']:
            func_args = getattr(record, 'func_args', ())
            if func_args:
                args_str += f"{func_args}"
        
        if detail['show_kwargs']:
            func_kwargs = getattr(record, 'func_kwargs', {})
            if func_kwargs:
                args_str += (", " if args_str else "") + f"{func_kwargs}"
        
        if args_str:
            return f"{func_name}({args_str})"
        return func_name
    
    def format_message(self, record, msg):
        if '\n' in msg:
            return "\n  " + msg.replace('\n', '\n  ')
        return msg
    
    def format_result(self, record, result):
        return f"结果:{result}"
    
    def format_exception(self, record):
        return self.formatException(record.exc_info)

class EnhancedColoredFormatter(BaseFormatter, logging.Formatter):
    """Colored text formatter"""
    COLOR_MAP = {
        logging.DEBUG: Fore.CYAN + Style.DIM,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }
    
    def format_time(self, record):
        return f"{Fore.LIGHTBLACK_EX}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}"
    
    def format_level(self, record):
        color = self.COLOR_MAP.get(record.levelno, Fore.WHITE)
        return f"{color}{record.levelname}{Style.RESET_ALL}"
    
    def format_name(self, record):
        return f"{Fore.WHITE}{record.name}{Style.RESET_ALL}"
    
    def format_event_id(self, record, event_id):
        return f"[EVENT {Fore.BLUE}{event_id}{Style.RESET_ALL}]"
    
    def format_func_info(self, record, func_name, detail):
        args_str = ""
        if detail['show_args']:
            func_args = getattr(record, 'func_args', ())
            if func_args:
                args_str += f"{Fore.CYAN}{func_args}{Style.RESET_ALL}"
        
        if detail['show_kwargs']:
            func_kwargs = getattr(record, 'func_kwargs', {})
            if func_kwargs:
                args_str += (", " if args_str else "") + f"{Fore.CYAN}{func_kwargs}{Style.RESET_ALL}"
        
        func_str = f"{Fore.YELLOW}{func_name}{Style.RESET_ALL}"
        if args_str:
            return f"{func_str}({args_str})"
        return func_str
    
    def format_message(self, record, msg):
        if '\n' in msg:
            return "\n  " + msg.replace('\n', '\n  ')
        return msg
    
    def format_result(self, record, result):
        return f"结果:{Fore.GREEN}{result}{Style.RESET_ALL}"
    
    def format_exception(self, record):
        return f"{Fore.RED}{self.formatException(record.exc_info)}{Style.RESET_ALL}"

def create_logger(
    name: str,
    color: bool = True,
    level: LogLevelType = logging.INFO,
    propagate: bool = False,
    formatter_config: Optional[Dict] = None
) -> logging.Logger:
    """Create and configure a logger"""
    logger = logging.getLogger(name)
    
    # Set log level
    if isinstance(level, str):
        level = level.upper()
        logger.setLevel(getattr(logging, level, logging.INFO))
    else:
        logger.setLevel(level)
    
    logger.propagate = propagate
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    if color:
        formatter = EnhancedColoredFormatter(
            datefmt="%Y-%m-%d %H:%M:%S",
            **(formatter_config or {})
        )
    else:
        formatter = EnhancedPlainTextFormatter(
            datefmt="%Y-%m-%d %H:%M:%S",
            **(formatter_config or {})
        )
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addFilter(LogFilter())
    return logger

# --------------------------
# Event Loop Implementation
# --------------------------
class EventLoop:
    def __init__(
        self,
        num_workers: Optional[int] = None,
        logger: bool = True,
        color: bool = True,
        log_level: LogLevelType = logging.INFO,
        result_ttl: int = 600,
        cleanup_interval: int = 600,
        log_config: Optional[Dict] = None
    ):
        self.event_results = {}
        self.event_queue = queue.Queue()
        
        # Create two loggers - one for user tasks, one for internal operations
        self.task_logger = create_logger(
            "EventLoop.Tasks",
            color=color,
            level=log_level,
            propagate=False,
            formatter_config=log_config
        )
        
        self.internal_logger = create_logger(
            "EventLoop.Internal",
            color=color,
            level=logging.WARNING if logger else logging.CRITICAL,
            propagate=False,
            formatter_config=log_config
        )

        self.lock = threading.RLock()
        self.results_lock = threading.Lock()
        self.cleanup_lock = threading.Lock()
        self.results_condition = threading.Condition(self.results_lock)
        self.cleanup_condition = threading.Condition(self.cleanup_lock)

        self.num_workers = num_workers or (os.cpu_count() or 1)
        self.workers = []
        self.running = False

        self.result_ttl = timedelta(seconds=result_ttl)
        self.last_cleanup = datetime.now()
        self.cleanup_interval = cleanup_interval

    def cleanup_worker(self):
        """Worker thread for cleaning up old results"""
        while self.running:
            time.sleep(self.cleanup_interval)
            with self.cleanup_lock:
                self._auto_cleanup()

    def _auto_cleanup(self):
        """Clean up expired results based on TTL"""
        now = datetime.now()
        to_delete = []
        
        # Find expired results
        with self.results_lock:
            for eid, data in self.event_results.items():
                if now - data["create_time"] > self.result_ttl:
                    to_delete.append(eid)
        
        # Delete expired results
        with self.results_lock:
            for eid in to_delete:
                del self.event_results[eid]
            
        self.last_cleanup = now
        if to_delete:
            self.internal_logger.debug(f"Cleaned up {len(to_delete)} expired results")

    def start(self):
        """Start the thread pool"""
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
            self.internal_logger.info(f"Started thread pool with {self.num_workers} workers")

    def run_worker(self):
        """Worker thread main logic"""
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
        """Gracefully shutdown the thread pool"""
        with self.lock:
            self.running = False

        for _ in range(self.num_workers):
            self.event_queue.put((gen(), "stop"))
        
        for worker in self.workers:
            worker.join()
        self.workers.clear()
        self.event_queue.join()
        self.internal_logger.info("Thread pool stopped")

    def call_function(self, func: Callable, *args, **kwargs) -> Any:
        """Call a function with error handling"""
        if not callable(func):
            raise TypeError(f"Object {func} is not callable")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise e

    def process_event(self, event: Any) -> Any:
        """Process an event and return result or error dict"""
        try:
            if isinstance(event, tuple):
                func, args, kwargs = event
                return self.call_function(func, *args, **kwargs)
            else:
                return self.call_function(event)
        except Exception as e:
            return {"error": e}

    def add_event(self, func: Callable, *args, **kwargs) -> str:
        """Add an event and return its ID"""
        event_id = gen()
        with self.results_lock:
            self.event_results[event_id] = {
                "status": "pending", 
                "result": None,
                "create_time": datetime.now()
            }
        
        self.task_logger.info(
            "Task submitted",
            extra={
                "event_id": str(event_id),
                "func_name": func.__name__,
                "func_args": args,
                "func_kwargs": kwargs
            }
        )

        self.event_queue.put((event_id, (func, args, kwargs)))
        return event_id

    def get_event_result(self, event_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Get event result, waiting if not ready"""
        with self.results_condition:
            start_time = time.monotonic()
            if event_id not in self.event_results:
                raise EventLoopError(f"Event {event_id} does not exist")

            while self.event_results[event_id]["status"] == "pending":
                remaining = timeout - (time.monotonic() - start_time) if timeout else None
                if remaining and remaining <= 0:
                    raise TimeoutError(f"Timeout waiting for result ({timeout}s)")
                self.results_condition.wait(remaining)
        return self.event_results.pop(event_id)
    
    def polling_result(self, eid: str, sleep_func: Callable[[float], None] = time.sleep, timeout: float = 0.1) -> Dict[str, Any]:
        """Poll for event result"""
        while True:
            if self.event_results[eid]["status"] == "pending":
                sleep_func(timeout)
            else:
                return self.event_results.pop(eid)

    def _update_event_result(self, event_id: str, result: Any):
        """Update event result and notify waiting threads"""
        with self.results_condition:
            if isinstance(result, dict) and "error" in result:
                error = result["error"]
                self.event_results[event_id].update({
                    "status": "error", 
                    "result": error
                })
                self.task_logger.error(
                    "Task failed",
                    extra={
                        "event_id": str(event_id),
                        "func_name": "_update_event_result"
                    },
                    exc_info=(type(error), error, error.__traceback__) if isinstance(error, Exception) else None
                )
            else:
                self.event_results[event_id].update({
                    "status": "completed", 
                    "result": result
                })
                self.task_logger.info(
                    "Task completed",
                    extra={
                        "event_id": str(event_id),
                        "task_result": str(result)
                    }
                )
            self.results_condition.notify_all()

# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    # Configure root logger
    root_logger = create_logger("Global", level="INFO")
    root_logger.setLevel(logging.INFO)

    # Disable third-party library logs
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").propagate = False

    class TestService:
        def process_data(self, data: str, count: int):
            """Process data with given count"""
            time.sleep(0.1)  # Simulate work
            return f"Processed {data} {count} times"
        
        def validate_input(self, input_data: dict):
            """Validate input data"""
            if not input_data.get("required_field"):
                raise ValueError("Missing required_field")
            return True

    # Create event loop with custom log configuration
    event_loop = EventLoop(
        num_workers=4,
        logger=True,
        color=True,
        log_level="DEBUG",
        result_ttl=30,
        cleanup_interval=30
    )

    # Start the event loop
    event_loop.start()

    # Submit tasks
    service = TestService()
    tasks = [
        event_loop.add_event(service.process_data, "test", 3),
        event_loop.add_event(service.process_data, "another", 5),
        event_loop.add_event(service.validate_input, {"required_field": "value"}),
        event_loop.add_event(service.validate_input, {"missing": "field"})
    ]

    # Process results
    for task_id in tasks:
        try:
            result = event_loop.get_event_result(task_id, timeout=5)
            if result["status"] == "completed":
                root_logger.info(f"Task {task_id} completed: {result['result']}")
            else:
                root_logger.error(f"Task {task_id} failed: {result['result']}")
        except TimeoutError:
            root_logger.error(f"Task {task_id} timed out")
        except EventLoopError as e:
            root_logger.error(f"Error processing task {task_id}: {e}")

    # Shutdown
    event_loop.shutdown()