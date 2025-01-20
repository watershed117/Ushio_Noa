from dataclasses import dataclass, field
from typing import Dict, List
import subprocess
import base64
import os
from uuid import uuid4
import json
import requests
import queue
from typing import Union
import logging


class Base_llm:
    def __init__(self,
                 api_key: str,
                 base_url: str = "https://open.bigmodel.cn/api/paas/v4",
                 model: str = "glm-4-flash",
                 storage: str = "",
                 tools: list = [],
                 system_prompt: str = "",
                 limit: str = "128k",
                 proxy: dict = {
                     'http': 'http://127.0.0.1:7890',
                     'https': 'http://127.0.0.1:7890',
                 },
                 ):
        self.base_url = base_url
        self.model = model
        self.client = requests.Session()
        self.client.headers.update({"Authorization": f"Bearer {api_key}"})
        self.chat_history = []
        self.store_history = []
        self.storage = storage
        self.tools = tools
        self.len_map = {"8k": 8000, "16k": 16000,
                        "32k": 32000, "64k": 64000, "128k": 128000}
        self.max_len = self.len_map.get(limit, 128000)
        self.proxy = proxy

        self.event = queue.Queue()
        
        self.ready = False

        if not self.is_valid_path(storage):
            raise ValueError("storage path is not valid")
        if system_prompt:
            self.chat_history.append(
                {"role": "system", "content": system_prompt})
            self.store_history.append(
                {"role": "system", "content": system_prompt})

    def result_appender(func):  # type: ignore
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)  # type: ignore
            if not hasattr(self, "result"):
                return result
            self.result.put(result)
            self.ready = True
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
        if self.chat_history and self.chat_history[0].get("role") == "system":
            self.chat_history = [self.chat_history[0]]
            self.store_history = [self.store_history[0]]
        else:
            self.chat_history = []
            self.store_history = []

    @result_appender  # type: ignore
    def send(self, messages: Union[dict, list[dict]]):
        logging.info(f"send args: {messages}")
        url = f"{self.base_url}/chat/completions"
        with self.client as client:
            if isinstance(messages, dict):
                payload = {"model": self.model,
                           "messages": self.chat_history+[messages]}
            else:
                payload = {"model": self.model,
                           "messages": self.chat_history+messages}
            if self.tools:
                payload.update({"tools": self.tools})
            response = client.post(url, json=payload, proxies=self.proxy)
            if response.status_code == 200:
                if isinstance(messages, dict):
                    self.chat_history.append(messages)
                    self.store_history.append(messages)
                else:
                    self.chat_history += messages
                    self.store_history += messages
                result = response.json()
                total_tokens = result.get("usage").get("total_tokens")
                if total_tokens >= self.max_len:
                    self.del_earliest_history()
                message = result["choices"][0]["message"]
                self.chat_history.append(message)
                self.store_history.append(message)
                return message
            else:
                logging.info(f"{response.status_code} {response.text}")
                print(response.status_code, response.text)
                return None

    @result_appender  # type: ignore
    def save(self, id: str = ""):
        if not id:
            id = str(uuid4())
        logging.info(os.path.join(self.storage, f"{id}.json"))
        with open(os.path.join(self.storage, f"{id}.json"), "w", encoding="utf-8") as f:
            json.dump(self.store_history, f, ensure_ascii=False, indent=4)
        return id

    @result_appender  # type: ignore
    def load(self, id: str):
        with open(os.path.join(self.storage, f"{id}.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            self.chat_history = data.copy()
            self.store_history = data.copy()
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

    def tokenizer(self, data: list[dict[str, str]],
                  url: str = "https://open.bigmodel.cn/api/paas/v4/tokenizer",
                  model: str = "glm-4-plus"
                  ):

        with self.client as client:
            payload = {"model": model, "messages": data}
            response = client.post(url, json=payload, proxies=self.proxy)
            if response.status_code == 200:
                result = response.json()
                return result["usage"].get("prompt_tokens")
            else:
                return response.status_code, response.json()

    def del_earliest_history(self):
        user_index = -1
        assistant_index = -1

        for index, message in enumerate(self.chat_history):
            if message.get("role") == "user" and user_index == -1:
                user_index = index
            elif message.get("role") == "assistant" and assistant_index == -1:
                assistant_index = index

        if user_index != -1 and assistant_index != -1:
            del self.chat_history[user_index:assistant_index + 1]
            logging.info("调用限制器")

    def limiter(self):
        while True:
            tokens = self.tokenizer(self.chat_history)
            if isinstance(tokens, int) and tokens >= self.max_len:
                self.del_earliest_history()
            else:
                break

    def call_method(self, method_name: str, *args, **kwargs):
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                logging.info(f"call method {method_name}")
                return method(*args, **kwargs)
            else:
                logging.info(f"{method_name} not callable")
                return None
        else:
            logging.info(f"{method_name} not found")
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
        self.result = queue.Queue(1)
        while True:
            event = self.event.get()
            if event:
                self.process_event(event)

    def latest_tool_recall(self, messages: list[dict[str, str]], function_name: str = ""):
        tools = queue.Queue()
        if function_name:
            for message in reversed(messages):
                if message.get("role") == "assistant":
                    if message.get("tool_calls"):
                        for tool in message.get("tool_calls"):  # type: ignore
                            if tool.get("function"):  # type: ignore
                                if tool.get("function").get("name") == function_name:  # type: ignore
                                    tools.put(tool.get("function")) # type: ignore
                                    return tools
                                else:
                                    continue
                            else:
                                continue
                        if tools.empty():
                            continue
                    else:
                        continue
                else:
                    continue
            if tools.empty():
                return None
        else:
            for message in reversed(messages):
                if message.get("role") == "assistant":
                    if message.get("tool_calls"):
                        for tool in message.get("tool_calls"):  # type: ignore
                            if tool.get("function"):  # type: ignore
                                tools.put(tool.get("function"))  # type: ignore
                            else:
                                continue
                        if not tools.empty():
                            return tools
                        else:
                            return None
                    else:
                        continue
                else:
                    continue

    def get_latest_message(self, messages: list[dict[str, str]]):
        for message in reversed(messages):
            if message.get("role") == "assistant":
                if message.get("content"):
                    return message.get("content")
        return None


@dataclass
class File_Format:
    image: List[str]
    audio: List[str]


ChatGPT = File_Format(image=[".png", ".jpeg", ".jpg", ".webp", ".gif"],
                      audio=[".wav", ".mp3"]
                      )
Gemini = File_Format(
    image=[".png", ".jpeg", ".jpg", ".webp", ".heic", ".heif"],
    audio=[".wav", ".mp3", ".aiff", ".aac", ".ogg", ".flac"]

)


class MessageGenerator:
    def __init__(self, format: str = "openai", file_format=ChatGPT, ffmpeg_path: str = "ffmpeg"):
        self.format = format
        self.file_format = file_format
        self.ffmpeg_path = ffmpeg_path

    def get_file_format(self, file_path: str):
        return os.path.splitext(file_path)[-1].lower()

    def audio_to_base64(self, file_path: str):
        if self.get_file_format(file_path) not in self.file_format.audio:
            file_path = self.ffmpeg_convert(file_path, ".wav")
        with open(file_path, "rb") as audio_file:
            encoded_string = base64.b64encode(
                audio_file.read()).decode('utf-8')
        return encoded_string

    def image_to_base64(self, file_path):
        if self.get_file_format(file_path) not in self.file_format.image:
            file_path = self.ffmpeg_convert(file_path, ".png")
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(
                image_file.read()).decode('utf-8')
        return encoded_string

    def ffmpeg_convert(self, file_path: str, target_format: str, target_path: str = ""):
        if not target_path:
            target_path = file_path.rsplit('.', 1)[0] + target_format
        else:
            if not os.path.isfile(target_path):
                raise ValueError("target_path is not a valid file path")
        try:
            process = subprocess.Popen(
                [self.ffmpeg_path, '-i', file_path, target_path],
            )
            process.wait()
            process.terminate()
            
            return target_path
        except subprocess.CalledProcessError as e:
            raise ValueError(
                f"Error converting file {file_path} to {target_format}: {e}")
            # return False

    def gen_user_msg(self, text: str, file_path: Union[str, list[str]] = ""):
        if self.format == "openai":
            payload = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                    ],
                }
            ]
            if isinstance(file_path, list):
                for file in file_path:
                    if self.get_file_format(file) in self.file_format.image:
                        payload[0]["content"].append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/{self.get_file_format(file)[1:]};base64,"
                                          + self.image_to_base64(file)},
                        })
                    elif self.get_file_format(file) in self.file_format.audio:
                        payload[0]["content"].append({
                            "type": "input_audio",
                        "input_audio": {"data": self.audio_to_base64(file),
                                        "format": self.get_file_format(file)[1:]}
                        })
            else:
                if self.get_file_format(file_path) in self.file_format.image:
                    payload[0]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{self.get_file_format(file_path)[1:]};base64,"
                                      + self.image_to_base64(file_path)},
                    })
                elif self.get_file_format(file_path) in self.file_format.audio:
                    payload[0]["content"].append({
                        "type": "input_audio",
                        "input_audio": {"data": self.audio_to_base64(file_path),
                                        "format": self.get_file_format(file_path)[1:]}
                    })
            return payload


if __name__ == "__main__":
    # chat = Base_llm(base_url="https://api.deepseek.com",
    #                 model="deepseek-chat",
    #                 api_key="sk-63bcccdd316243aeac4e8cc5fcf5d8a1",
    #                 storage=r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\history",
    #                 proxy=None)  # type: ignore

    # result = chat.send({"role": "user", "content": "你好"})
    # print(result)
    # result = chat.send({"role": "user", "content": "你好"})
    # print(result)

    chat = Base_llm(base_url="https://gemini.watershed.ip-ddns.com/v1",
                    model="gemini-1.5-flash",
                    api_key="AIzaSyAv6RumkrxIvjLKgtiE-UceQODvvbTMd0Q",
                    storage=r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\history",
                    system_prompt="使用中文回复",
                    proxy=None)  # type: ignore

    message_generator = MessageGenerator(
        format="openai", file_format=Gemini, ffmpeg_path="ffmpeg")

    message=message_generator.gen_user_msg("图片里有什么",['C:\\Users\\water\\Desktop\\cover.png'])
    result = chat.send(messages=message)  # type: ignore
    print(result)

    chat.clear_history()
    print("history cleared")

    message = message_generator.gen_user_msg(
        "将音频转换为文字", [r"D:\storage\Desktop 2024.10.14 - 22.31.37.04.DVR.mp3"])
    result = chat.send(messages=message)  # type: ignore
    print(result)
