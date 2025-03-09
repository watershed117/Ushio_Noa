import queue
import threading
import uuid
from typing import Any, Callable, Dict, Union
import logging
from colorama import Fore, Style, init
import inspect

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """自定义日志格式，添加颜色"""
    COLORS = {
        logging.DEBUG: Fore.CYAN + Style.DIM,               # 调试信息：青色+暗淡
        logging.INFO: Fore.GREEN,                           # 普通信息：绿色
        logging.WARNING: Fore.YELLOW,                       # 警告信息：黄色
        logging.ERROR: Fore.RED,                            # 错误信息：红色
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,      # 严重错误：品红+高亮
    }

    def format(self, record):
        # 获取日志级别对应的颜色
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        # 格式化日志消息
        message = super().format(record)
        # 添加颜色
        return color + message + Style.RESET_ALL

# 配置日志
def setup_logging(name: str , color: bool = True):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # 关键修复：禁止传播到父记录器

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 设置自定义的彩色格式
    if color:
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    console_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(console_handler)

    return logger

class EventLoopError(Exception):
    """事件循环异常基类"""
    pass

class MethodNotFoundError(EventLoopError):
    """方法不存在异常"""
    def __init__(self, method_name: str):
        super().__init__(f"Method '{method_name}' not found")
        self.method_name = method_name

class InvalidArgumentsError(Exception):
    def __init__(self, func_name: str, message: str):
        super().__init__(f"Invalid arguments for '{func_name}': {message}")
        self.func_name = func_name
        self.message = message

class EventLoop:
    def __init__(self,
                 validate_arguments: bool = True):
        self.validate_arguments = validate_arguments
        self.event_results = {}
        self.event_queue = queue.Queue()
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.logger = setup_logging("EventLoop")  # 初始化彩色日志

    def _validate_arguments(self, func: Callable, *args, **kwargs) -> None:
        """验证函数参数的类型和数量"""
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for name, value in bound_args.arguments.items():
            param = sig.parameters[name]
            if param.annotation != inspect.Parameter.empty:
                if not isinstance(value, param.annotation):
                    raise InvalidArgumentsError(
                        func_name=func.__name__,
                        message=f"参数 '{name}' 需要 {param.annotation} 类型，实际得到 {type(value)} 类型"
                    )

    def call_function(self, func: Callable, *args, **kwargs) -> Any:
        """调用函数并处理异常及参数验证"""
        if not callable(func):
            raise TypeError(f"传入的对象 {func} 不可调用")
        
        try:
            # 验证参数
            if self.validate_arguments:
                self._validate_arguments(func, *args, **kwargs)
            return func(*args, **kwargs)
        except InvalidArgumentsError as e:
            raise e
        except Exception as e:
            raise e

    def process_event(self, event: Any) -> Any:
        """处理事件并返回结果或异常字典"""
        try:
            if isinstance(event, tuple):
                func, args, kwargs = event  # 解包 args 和 kwargs
                return self.call_function(func, *args, **kwargs)
            else:
                return self.call_function(event)
        except Exception as e:
            # 发生异常时返回包含错误信息的字典
            return {"error": e}

    def add_event(self, func: Union[Callable, str], *args, **kwargs) -> uuid.UUID:
        """添加事件并返回UUID作为ID"""
        event_id = uuid.uuid4()
        with self.lock:
            self.event_results[event_id] = {"status": "pending", "result": None}
        if isinstance(func, str):
            self.event_queue.put((event_id, func))
        else:
            self.event_queue.put((event_id, (func, args, kwargs)))  # 传递 args 和 kwargs
        return event_id

    def get_event_result(self, event_id: uuid.UUID) ->Dict[str, Any]:
        """获取结果，如果结果未就绪则等待"""
        with self.condition:
            if event_id not in self.event_results:
                raise EventLoopError(f"Event {event_id} does not exist or has been removed")

            # 等待事件完成的通知
            while self.event_results[event_id]["status"] == "pending":
                self.condition.wait()  # 释放锁并等待，收到通知后重新获取锁

            result = {
                "status": self.event_results[event_id]["status"],
                "result": self.event_results[event_id]["result"],
            }
            del self.event_results[event_id]  # 删除结果
            return result
        
    def run(self):
        """事件循环主逻辑"""
        while True:
            event_id, event = self.event_queue.get()
            self.logger.debug(f"\n{Fore.BLUE}事件 {event_id} 开始处理: \n{event[0].__name__}\nargs: {event[1]}\nkwargs: {event[2]}{Style.RESET_ALL}")
            try:
                if event == "stop":
                    # 处理剩余事件
                    while not self.event_queue.empty():
                        next_event_id, next_event = self.event_queue.get()
                        if next_event == "stop":
                            continue  # 忽略额外的停止事件
                        result = self.process_event(next_event)
                        self._update_event_result(next_event_id, result)
                    break  # 退出主循环

                result = self.process_event(event)
                self._update_event_result(event_id, result)

            finally:
                self.event_queue.task_done()

        self.logger.info(f"\n{Fore.RED}事件循环停止")

    def _update_event_result(self, event_id: uuid.UUID, result: Any):
        """更新事件结果并通知等待的线程"""
        with self.condition:
            if isinstance(result, dict) and len(result) == 1 and "error" in result:
                self.event_results[event_id] = {"status": "error", "result": result.get("error")}
                self.logger.error(f"\n事件 {event_id} 处理失败: \n{result.get('error')}")
            else:
                self.event_results[event_id] = {"status": "completed", "result": result}
                self.logger.debug(f"\n{Fore.GREEN}事件 {event_id} 处理成功: \n结果: {result}")
            self.condition.notify_all()  # 通知所有等待的线程
            self.logger.debug(f"\n{Fore.BLUE}事件 {event_id} 已处理")


if __name__ == "__main__":
    import time
    logger = setup_logging("root", False)

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
    event_loop = EventLoop()
    t = threading.Thread(target=event_loop.run, daemon=True)
    t.start()

    # 提交测试用例
    event_ids = []
    event_ids.append(event_loop.add_event(test_instance.test_method, 1, 2))              # 正常调用
    event_ids.append(event_loop.add_event(test_instance.test_method, arg1=3,arg2=4))     # 关键字参数调用
    event_ids.append(event_loop.add_event(test_instance.test_method2))                   # 无参方法
    event_ids.append(event_loop.add_event(test_instance.test_method, 1))                 # 参数不足
    event_ids.append(event_loop.add_event(test_instance.test_method, "a", "b"))          # 错误参数类型
    event_ids.append(event_loop.add_event(test_instance.long_time_task))                 # 耗时任务

    # 等待测试用例处理完成
    for eid in event_ids[:]:
        result = event_loop.get_event_result(eid)
        if result["status"] == "error":
            logger.error(f"\n事件 {eid} 处理失败: {result['result']}")
            pass
        else:
            logger.info(f"\n事件 {eid} 已处理，结果: {result['result']}")
            pass
        event_ids.remove(eid)  # 移除已处理的事件ID

    logger.info("\n所有事件处理完成")
    if not event_loop.event_results:
        logger.info("\nevent_results已处理完成")
    else:
        logger.error("\nevent_results存在未处理的结果")
        logger.error(event_loop.event_results)

    # 发送停止事件
    event_loop.add_event("stop")
    t.join(timeout=1)