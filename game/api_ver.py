import os
from uuid import uuid4
import json
import requests
import queue


class ChatGLM:
    def __init__(self, api_key: str, model: str = "glm-4-flash", storage: str = "", tools: list = [], system_prompt: str = "", limit: str = "128k"):
        self.model = model
        self.client = requests.Session()
        self.client.headers.update({"Authorization": f"Bearer {api_key}"})
        self.history = []
        self.history_storage = []
        self.storage = storage
        self.tools = tools
        self.len_map = {"8k": 8000, "16k": 16000,
                        "32k": 32000, "64k": 64000, "128k": 128000}
        self.max_len = self.len_map.get(limit, 128000)
        self.event = queue.Queue()
        self.result = queue.Queue(1)
        self.ready = False

        if not self.is_valid_path(storage):
            raise ValueError("storage path is not valid")
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})
            self.history_storage.append(
                {"role": "system", "content": system_prompt})

    def result_appender(func):  # type: ignore
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)  # type: ignore
            self.result.put(result)
            self.ready = True
            return result
        return wrapper

    def is_valid_path(self, path_str: str):
        try:
            os.path.exists(path_str)
            return True
        except Exception:
            return False

    def get_creation_time(self, file_path):
        return os.path.getctime(file_path)

    def clear_history(self):
        self.history = [self.history[0]]
        self.history_storage = [self.history_storage[0]]

    @result_appender  # type: ignore
    def send(self, messages: dict):
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        with self.client as client:
            self.history.append(messages)
            self.history_storage.append(messages)
            payload = {"model": self.model, "messages": self.history}
            if self.tools:
                payload.update({"tools": self.tools})
            response = client.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                print(result)
                total_tokens = result.get("usage").get("total_tokens")
                if total_tokens >= self.max_len:
                    self.limiter()
                content = result["choices"][0]["message"]
                if content.get("content") or content.get("tool_calls"):
                    if content.get("tool_calls"):
                        self.history.append({"role": content.get(
                            "role"), "tool_calls": content.get("tool_calls")})
                        self.history_storage.append(
                            {"role": content.get("role"), "tool_calls": content.get("tool_calls")})
                    else:
                        self.history.append({"role": content.get(
                            "role"), "content": content.get("content")})
                        self.history_storage.append(
                            {"role": content.get("role"), "content": content.get("content")})
                return content
            else:
                return response.status_code, response.json()

    @result_appender  # type: ignore
    def save(self):
        id = str(uuid4())
        print(os.path.join(self.storage, f"{id}.json"))
        with open(os.path.join(self.storage, f"{id}.json"), "w", encoding="utf-8") as f:
            json.dump(self.history_storage, f, ensure_ascii=False, indent=4)
        return id

    @result_appender  # type: ignore
    def load(self, id: str):
        with open(os.path.join(self.storage, f"{id}.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            self.history = data
            self.history_storage = data
            tokens = self.tokenizer(data)
            if isinstance(tokens, int):
                if tokens >= self.max_len:
                    self.limiter()
            return id

    def sort_files(self, folder_path):
        # 获取文件夹下的所有文件
        files = [os.path.join(folder_path, f) for f in os.listdir(
            folder_path) if f.endswith('.json')]

        # 根据创建时间排序
        files.sort(key=self.get_creation_time, reverse=True)
        return files

    @result_appender  # type: ignore
    def get_conversations(self):
        files = self.sort_files(self.storage)
        conversations = []
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                message_exist = False
                for message in data:
                    if message.get("role") == "user":
                        conversations.append({"title": message.get("content")[
                                             :10], "id": os.path.basename(file_path)[:-5]})
                        message_exist = True
                        break
                if not message_exist:
                    conversations.append(
                        {"title": None, "id": os.path.basename(file_path)[:-5]})
        return conversations

    @result_appender  # type: ignore
    def delete_conversation(self, id: str):
        file_path = os.path.join(self.storage, f"{id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False

    def tokenizer(self, data: list[dict[str, str]]):
        url = "https://open.bigmodel.cn/api/paas/v4/tokenizer"
        with self.client as client:
            payload = {"model": self.model, "messages": data}
            response = client.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result["usage"].get("prompt_tokens")
            else:
                return response.status_code, response.json()

    def limiter(self):
        while True:
            tokens = self.tokenizer(self.history)
            if isinstance(tokens, int) and tokens >= self.max_len:
                self.history = self.history[:1] + self.history[3:]
            else:
                break

    def call_method(self, method_name: str, *args, **kwargs):
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                print(f"call method {method_name}")
                return method(*args, **kwargs)
            else:
                print(f"{method_name} not callable")
                return None
        else:
            print(f"{method_name} not found")
            return None

    def process_event(self, event):
        """
        处理事件，根据事件类型调用相应的方法。

        参数:
            event: 可以是字符串（方法名）或元组 (method_name, args, kwargs)。

        返回:
            方法调用的结果或 None。
        """
        if isinstance(event, str):  # 事件是一个方法名字符串
            return self.call_method(event)
        elif isinstance(event, tuple) and len(event) > 0:  # 事件是一个元组
            method_name = event[0]  # 第一个元素是方法名
            if len(event) == 1:  # 只有方法名，无参数
                return self.call_method(method_name)
            elif len(event) == 2:  # 方法名和参数
                if isinstance(event[1], dict):  # 第二个元素是字典，作为 kwargs 处理
                    return self.call_method(method_name, **event[1])
                elif isinstance(event[1], tuple):  # 第二个元素是元组，作为 args 处理
                    return self.call_method(method_name, *event[1])
            elif len(event) == 3:  # 方法名、args 和 kwargs
                args = event[1] if isinstance(event[1], tuple) else ()
                kwargs = event[2] if isinstance(event[2], dict) else {}
                return self.call_method(method_name, *args, **kwargs)
        return None

    def run(self):
        while True:
            event = self.event.get()
            if event:
                self.process_event(event)

    def latest_tool_recall(self, messages: list[dict[str, str]]):
        for message in reversed(messages):
            if message.get("role") == "assistant":
                if message.get("tool_calls"):
                    tools = []
                    for tool in message.get("tool_calls"):  # type: ignore
                        if tool.get("function"):  # type: ignore
                            tools.append(tool.get("function"))  # type: ignore
                    return tools

    def get_latest_message(self, messages: list[dict[str, str]]):
        for message in reversed(messages):
            if message.get("role") == "assistant":
                if message.get("content"):
                    return message.get("content")
        return None


if __name__ == "__main__":
    tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "control_character",
                        "description": "控制角色的立绘，表情，动作，特效，在人物情绪变化时调用",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "position": {
                                    "type": "string",
                                    "description": "显示立绘的位置，将屏幕水平分为五等份，从左向右位置分别命名为'1'~'5'"
                                },
                                "emotion": {
                                    "type": "string",
                                    "description": "要显示的立绘的表情，可选'joy','sadness','anger','surprise','fear','disgust','normal','embarrassed'"
                                },
                                "emoji": {
                                    "type": "string",
                                    "description": "要显示的表情符号动画，可选'angry','bulb','chat','dot','exclaim','heart','music','question','respond','sad','shy','sigh','steam','surprise','sweat','tear','think','twinkle','upset','zzz'"
                                },
                                "action": {
                                    "type": "string",
                                    "description": "要播放的动作，可选'sightly_down','fall_left','fall_right','jump','jump_more'"
                                },
                                "effect": {
                                    "type": "string",
                                    "description": "要附加在立绘上的特效，可选'scaleup','hide','holography'"
                                }
                            },
                            "required": ["position", "emotion"]
                        }
                    }
                }
            ]
    with open(r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\test.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    chat = ChatGLM(api_key="6b98385d296d8687ec15b54faa43a01c.43RrndejVMU5KmJE",
                   model="glm-4-flash",
                   system_prompt=prompt,
                   storage="your_storage_path",
                   tools=tools)

    print(chat.tokenizer([{"role": "user", "content": prompt}]))
    chat.send({"role": "user", "content": "你好"})
