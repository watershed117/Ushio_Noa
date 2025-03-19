from dataclasses import dataclass
from typing import List
import subprocess
import base64
from uuid import uuid4
import json
import requests
from typing import Union,Callable
import logging
import pathlib

class HTTPException(Exception):
    """
    自定义异常类，用于处理HTTP请求中非200状态码的情况。
    
    属性:
        status_code (int): HTTP响应状态码。
        message (str): 异常信息。
        response (str): HTTP响应内容。
    """
    
    def __init__(self, status_code, response=None, message=None):
        """
        初始化异常类。
        
        参数:
            status_code (int): HTTP响应状态码。
            response (str, optional): HTTP响应内容。默认为 None。
            message (str, optional): 自定义异常信息。默认为 None。
        """
        self.status_code = status_code
        self.response = response
        self.message = message or f"HTTP请求失败，状态码: {status_code}"
        super().__init__(self.message)
    
    def __str__(self):
        """
        返回异常的字符串表示。
        """
        return f"{self.message}\n状态码: {self.status_code}\n响应内容: {self.response}"


class Base_llm:
    """
    基础大语言模型类，用于与API进行交互并管理聊天历史记录。

    :param api_key: API密钥
    :param base_url: API的基础URL，默认为"https://open.bigmodel.cn/api/paas/v4"
    :param model: 使用的模型名称，默认为"glm-4-flash"
    :param storage: 聊天记录存储路径，默认为空
    :param tools: 工具列表，默认为空
    :param system_prompt: 系统提示，默认为空
    :param limit: 聊天记录的最大长度限制，默认为"128k"
    :param proxy: 代理设置，默认为本地代理
    :param tool_collection: 一个tool集合的类对象实例，类方法需要和tools入参中定义的函数名一致
    """
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
                 tool_collection: object = None
                 ):
        self.base_url = base_url
        self.model = model
        self.client = requests.Session()
        self.client.headers.update({"Authorization": f"Bearer {api_key}"})
        self.chat_history = []
        self.store_history = []
        if storage:
            try:
                self.storage = pathlib.Path(storage)
            except Exception:
                raise ValueError("storage path is not valid")
        else:
            self.storage = None
        self.tools = tools
        self.len_map = {"8k": 8000, "16k": 16000,
                        "32k": 32000, "64k": 64000, "128k": 128000}
        self.max_len = self.len_map.get(limit, 128000)
        self.proxy = proxy
        self.tool_collection = tool_collection

        if system_prompt:
            self.chat_history.append(
                {"role": "system", "content": system_prompt})
            self.store_history.append(
                {"role": "system", "content": system_prompt})

    def clear_history(self):
        """
        清除聊天历史记录，保留系统提示（如果有）。
        """
        if self.chat_history and self.chat_history[0].get("role") == "system":
            self.chat_history = [self.chat_history[0]]
            self.store_history = [self.store_history[0]]
        else:
            self.chat_history = []
            self.store_history = []

    def send(self, messages: Union[dict, list[dict]],usage : bool = False, **kwargs) -> dict:
        """
        发送消息到API并获取响应。

        :param messages: 要发送的消息，可以是单个消息或消息列表
        :return: API返回的消息
        """
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
            payload.update(kwargs)
            try:
                response = client.post(url, json=payload, proxies=self.proxy)
            except Exception as e:
                raise e
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
                print(message)
                self.chat_history.append(message)
                self.store_history.append(message)
                if usage:
                    message.update(result.get("usage"))
                return message
            else:
                try:
                    error_info = response.json()
                except Exception:
                    error_info = response.text
                raise HTTPException(response.status_code, error_info)

    def save(self, id: str = ""):
        """
        保存当前聊天记录到文件。

        :param id: 文件ID，如果未提供则生成一个UUID
        :return: 文件ID
        """
        if not self.storage:
            raise ValueError("storage path is not valid")
        if not id:
            id = str(uuid4())
        save_path = self.storage / f"{id or uuid4()}.json"
        with save_path.open("w", encoding="utf-8") as f:
            json.dump(self.store_history, f, ensure_ascii=False, indent=4)
        return id

    def load(self, id: str):
        """
        从文件加载聊天记录。

        :param id: 文件ID
        :return: 文件ID
        """
        if not self.storage:
            raise ValueError("storage path is not valid")
        load_path = self.storage / f"{id}.json"
        with load_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            self.chat_history = data.copy()
            self.store_history = data.copy()
            tokens = self.tokenizer(data)
            if isinstance(tokens, int):
                if tokens >= self.max_len:
                    self.limiter()
            return id

    def sort_files(self, folder_path: str = ""):
        """
        对文件夹中的文件按创建时间进行排序。

        :param folder_path: 文件夹路径，如果未提供则使用存储路径
        :return: 排序后的文件路径列表
        """
        if folder_path:
            target_dir = pathlib.Path(folder_path)
        elif self.storage:
            target_dir = self.storage
        else:
            raise ValueError("storage path is not valid")
        if not target_dir.exists() or not target_dir.is_dir():
            raise ValueError(f"The path {target_dir} does not exist or is not a directory.")
        files = sorted(target_dir.glob("*.json"), 
                      key=lambda x: x.stat().st_ctime, 
                      reverse=True)
        return [f.as_posix() for f in files]

    def get_conversations(self):
        """
        获取所有对话记录。

        :return: 对话记录列表，包含标题和ID
        """
        if not self.storage:
            raise ValueError("storage path is not valid")
        files = self.sort_files(self.storage.as_posix())
        conversations = []
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                message_exist = False
                for message in data:
                    if message.get("role") == "user":
                        conversations.append({"title": message.get("content","")[
                                             :10], "id": pathlib.Path(file_path).name[:-5]})
                        message_exist = True
                        break
                if not message_exist:
                    conversations.append(
                        {"title": "", "id": pathlib.Path(file_path).name[:-5]})
        return conversations

    def delete_conversation(self, id: str):
        """
        删除指定的对话记录。

        :param id: 对话记录ID
        :return: 是否删除成功
        """
        if not self.storage:
            raise ValueError("storage path is not valid")
        target_file = self.storage / f"{id}.json"
        if target_file.exists():
            target_file.unlink()
            return True
        return False

    def tokenizer(self, data: list[dict[str, str]],
                  url: str = "https://open.bigmodel.cn/api/paas/v4/tokenizer",
                  model: str = "glm-4-plus"
                  ):
        """
        计算消息的token数量。

        :param data: 消息列表
        :param url: tokenizer的URL
        :param model: 使用的模型
        :return: token数量或错误信息
        """
        with self.client as client:
            payload = {"model": model, "messages": data}
            response = client.post(url, json=payload, proxies=self.proxy)
            if response.status_code == 200:
                result = response.json()
                return result["usage"].get("prompt_tokens")
            else:
                return response.status_code, response.json()

    def del_earliest_history(self):
        """
        删除最早的聊天记录。
        """
        user_index = -1
        assistant_index = -1

        for index, message in enumerate(self.chat_history):
            if message.get("role") == "user" and user_index == -1:
                user_index = index
            elif message.get("role") == "assistant" and assistant_index == -1:
                assistant_index = index

        if user_index != -1 and assistant_index != -1:
            del self.chat_history[user_index:assistant_index + 1]

    def limiter(self):
        """
        限制聊天记录的长度，确保不超过最大token限制。
        """
        while True:
            tokens = self.tokenizer(self.chat_history)
            if isinstance(tokens, int) and tokens >= self.max_len:
                self.del_earliest_history()
            else:
                break

    def latest_tool_recall(self, messages: list[dict[str, str]], function_name: str = ""):
        """
        获取最近的工具调用记录。

        :param messages: 消息列表
        :param function_name: 工具函数名，如果未提供则返回所有工具调用记录
        :return: 工具调用记录列表
        """
        # 逆序遍历消息，寻找最近的工具调用记录
        for message in reversed(messages):
            if message.get("role") != "assistant":
                continue  # 只处理助手消息
            
            tool_calls = message.get("tool_calls")
            if not tool_calls:
                continue  # 跳过无工具调用的消息
            
            # 情况1：指定了特定工具函数名
            if function_name:
                for tool in tool_calls:
                    func = tool.get("function") # type: ignore
                    if func and func.get("name") == function_name:
                        return [func]  # 返回第一个匹配项
            
            # 情况2：未指定函数名，返回所有工具函数
            else:
                functions = [tool.get("function") for tool in tool_calls if tool.get("function")] # type: ignore
                if functions:
                    return functions  # 返回当前消息的所有函数
        
        return []  # 未找到任何记录

    def get_latest_message(self, messages: list[dict[str, str]]):
        """
        获取最新的助手消息。

        :param messages: 消息列表
        :return: 最新的助手消息内容
        """
        for message in reversed(messages):
            if message.get("role") == "assistant":
                if message.get("content"):
                    return message.get("content")
        return None
            
    def handle_message(self, handle_content: Callable, handle_tool_calls: Callable,callback: Union[Callable,None]=None)->Callable:
        """
        handle_content(content:str)
        handle_tool_calls(tool_calls:list[dict])
        """
        def processor(reply: dict):
            tool_messages=None
            if reply.get("role") == "assistant":
                if reply.get("content"):
                    handle_content(reply.get("content"))
                if reply.get("tool_calls"):
                    tool_messages=handle_tool_calls(reply.get("tool_calls"))
                if tool_messages:
                    if callback:
                        callback(self.send,tool_messages)
                    processor(self.send(tool_messages))
        return processor
        
    def handle_content(self, content: str):
        print(content)

    def handle_tool_calls(self, tool_calls: list[dict])->list[dict]:
        messages = []
        for tool in tool_calls:
            tool_call_id = tool.get("id")
            tool_data=tool.get("function")
            function_name = tool_data.get("name") # type: ignore
            try:
                if tool_data.get("arguments"): # type: ignore
                    kwargs = json.loads(tool_data.get("arguments"))  # type: ignore
                else:
                    kwargs = {}
            except:
                result = f"{function_name} arguments is not json valid"
                payload = {
                    "role": "tool",
                    "content": result,
                    "tool_call_id":tool_call_id 
                }
                messages.append(payload)
                continue

            if hasattr(self.tool_collection,function_name):
                func = getattr(self.tool_collection,function_name)
                if callable(func):
                    try:
                        print(f"调用函数{function_name}，参数{kwargs}")
                        result=func(**kwargs)
                        if not isinstance(result,str):
                            result = str(result)
                    except Exception as e:
                        result = str(e)
                else:
                    result = f"{function_name} is not callable"
            else:
                result = f"{function_name} does not exist"

            print(result)
            payload = {
                        "role": "tool",
                        "content": result,
                        "tool_call_id":tool_call_id 
                    }
            messages.append(payload)
        return messages
    
    def reply_json(self, json_schema:dict,messages: Union[dict, list[dict]],usage : bool = False,**kwargs) -> Union[dict,list]:
        """
        json_schema example:
        ```python
        response_format={
            "type": "json_schema",
            "json_schema": {
                "properties": {
                "text": {
                    "type": "string"
                }
                },
                "required": ["text"],
                "type": "object"
            },
            "strict": True
            }
        ```
        """
        data=self.send(messages=messages,usage=usage,response_format=json_schema,**kwargs)
        return json.loads(data.get("content",""))
    
    def terminal(self):
        """
        终端交互模式。
        """
        handler=self.handle_message(self.handle_content,self.handle_tool_calls)
        while True:
            user_input = input("User: ")
            if user_input == "exit":
                break
            reply = self.send({"role": "user", "content": user_input})
            handler(reply)
            
@dataclass
class File_Format:
    """
    文件格式类，用于定义支持的图像和音频文件格式。

    :param image: 支持的图像文件格式列表
    :param audio: 支持的音频文件格式列表
    """
    image: List[str]
    audio: List[str]


CHATGPT = File_Format(image=[".png", ".jpeg", ".jpg", ".webp", ".gif"],
                      audio=[".wav", ".mp3"],
                      )
GEMINI = File_Format(
    image=[".png", ".jpeg", ".jpg", ".webp", ".heic", ".heif"],
    audio=[".wav", ".mp3", ".aiff", ".aac", ".ogg", ".flac"],
)

class MessageGenerator:
    """
    消息生成器类，用于生成包含文本和文件的消息。

    :param format: 消息格式，默认为"openai"
    :param file_format: 文件格式类实例，默认为CHATGPT
    :param ffmpeg_path: ffmpeg路径，默认为"ffmpeg"
    """
    def __init__(self, format: str = "openai", file_format=CHATGPT, ffmpeg_path: str = "ffmpeg"):
        self.format = format
        self.file_format = file_format
        self.ffmpeg_path = ffmpeg_path

    def get_file_format(self, file_path: str):
        """
        获取文件的扩展名。

        :param file_path: 文件路径
        :return: 文件扩展名
        """
        return pathlib.Path(file_path).suffix.lower()

    def get_file_type(self, file_path: str):
        """
        获取文件类型（图像或音频）。

        :param file_path: 文件路径
        :return: 文件类型（"image" 或 "audio"），如果格式不支持则返回 False
        """
        format = self.get_file_format(file_path)
        if format in self.file_format.image:
            return "image"
        elif format in self.file_format.audio:
            return "audio"
        else:
            return False

    def audio_to_base64(self, file_path: str):
        """
        将音频文件转换为Base64编码。

        :param file_path: 音频文件路径
        :return: Base64编码的音频数据
        """
        if self.get_file_format(file_path) not in self.file_format.audio:
            file_path = self.ffmpeg_convert(file_path, ".wav")
        with open(file_path, "rb") as audio_file:
            encoded_string = base64.b64encode(
                audio_file.read()).decode('utf-8')
        return encoded_string

    def image_to_base64(self, file_path):
        """
        将图像文件转换为Base64编码。

        :param file_path: 图像文件路径
        :return: Base64编码的图像数据
        """
        if self.get_file_format(file_path) not in self.file_format.image:
            file_path = self.ffmpeg_convert(file_path, ".png")
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(
                image_file.read()).decode('utf-8')
        return encoded_string

    def ffmpeg_convert(self, file_path: str, target_format: str, target_path: str = ""):
        """
        使用ffmpeg转换文件格式。

        :param file_path: 原始文件路径
        :param target_format: 目标文件格式
        :param target_path: 目标文件路径，如果未提供则使用原始文件路径
        :return: 转换后的文件路径
        """
        if not target_path:
            target_path = file_path.rsplit('.', 1)[0] + target_format
        else:
            tmp = pathlib.Path(target_path)
            if not tmp.exists() or not tmp.is_dir():
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

    def gen_user_msg(self, text: str, file_path: Union[str, list[str]] = ""):
        """
        生成用户消息，支持文本和文件（图像或音频）。

        :param text: 文本内容
        :param file_path: 文件路径，可以是单个文件路径或文件路径列表
        :return: 生成的消息内容
        """
        if self.format == "openai":
            payload = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                    ],
                }
            ]
            if not file_path:
                return payload
            if isinstance(file_path, list):
                for file in file_path:
                    format = self.get_file_format(file)
                    if format in self.file_format.image:
                        payload[0]["content"].append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/{self.get_file_format(file)[1:]};base64,"
                                          + self.image_to_base64(file)},
                        })
                    elif format in self.file_format.audio:
                        payload[0]["content"].append({
                            "type": "input_audio",
                            "input_audio": {"data": self.audio_to_base64(file),
                                            "format": self.get_file_format(file)[1:]}
                        })
                    else:
                        raise ValueError(
                            f"file {file} format {format} is not supported")
            else:
                format = self.get_file_format(file_path)
                if format in self.file_format.image:
                    payload[0]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{format[1:]};base64,"
                                      + self.image_to_base64(file_path)},
                    })
                elif format in self.file_format.audio:
                    payload[0]["content"].append({
                        "type": "input_audio",
                        "input_audio": {"data": self.audio_to_base64(file_path),
                                        "format": self.get_file_format(file_path)[1:]}
                    })
                else:
                    raise ValueError(
                        f"file {file_path} format {format} is not supported")
            return payload
        else:
            raise ValueError(f"format {self.format} is not supported")

class DeepSeek(Base_llm):
    def list_models(self):
        url = f"{self.base_url}/models"
        response = self.client.get(url, proxies=self.proxy)
        if response.status_code == 200:
            result = response.json()
            return result.get("data")
        else:
            return response.status_code, response.json()
        
class Gemini(Base_llm):
    def list_models(self):
        """
        获取模型列表。

        :return: 模型列表
        """
        url = f"{self.base_url}/models"
        try:
            response = self.client.get(url,proxies=self.proxy)
        except Exception as e:
            raise e
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            try:
                error_info = response.json()
            except Exception:
                error_info = response.text
            raise HTTPException(response.status_code, error_info)
        
if __name__ == "__main__":
#https://r.aya1.de/aya/https/gemini.watershed.ip-ddns.com/v1
#https://gemini.watershed.ip-ddns.com/v1
    tools = [
        {
            "type": "function",
            "function": {
                "name": "agent_commander",
                "description": "send command to agent with a collection of tools",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Natural Language message to send to agent",
                        },
                        "files": {
                            "type": "array",
                            "description": "full file paths",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": ["message"],
                },
            }
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add",
                "description": "Add two numbers and return the sum.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {
                            "type": "number",
                            "description": "The first number to add.",
                        },
                        "num2": {
                            "type": "number",
                            "description": "The second number to add.",
                        }
                    },
                    "required": ["num1", "num2"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "subtract",
                "description": "Subtract the second number from the first number and return the difference.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {
                            "type": "number",
                            "description": "The number to subtract from.",
                        },
                        "num2": {
                            "type": "number",
                            "description": "The number to subtract.",
                        }
                    },
                    "required": ["num1", "num2"],
                },
            }
        }
    ]

    class ToolCollection:
        @staticmethod
        def add(num1: float, num2: float) -> float:
            """
            加法运算：返回两个数字的和。
            """
            return num1 + num2

        @staticmethod
        def subtract(num1: float, num2: float) -> float:
            """
            减法运算：返回第一个数字减去第二个数字的结果。
            """
            return num1 - num2
    
    chat = Gemini(base_url="https://generativelanguage.googleapis.com/v1beta/openai",
                    model="gemini-2.0-flash",
                    api_key="AIzaSyAv6RumkrxIvjLKgtiE-UceQODvvbTMd0Q",
                    storage=r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\history",
                    system_prompt="使用中文回复",
                    tools=tools,
                    tool_collection=ToolCollection()
                    )  # type: ignore
    
    # result = chat.list_models()
    # print(result)

    message_generator = MessageGenerator(
        format="openai", file_format=GEMINI, ffmpeg_path="ffmpeg")

    response_format={
        "type": "json_schema",
        "json_schema": {
        "schema": {
            "properties": {
            "text": {
                "type": "string"
            },
            "emotion": {
                "type": "string",
                "enum":["joy", "sadness", "anger", "surprise", "fear", "disgust", "normal", "embarrassed"]
            },
            },
            "required": ["text", "emotion"],
            "type": "object",
        },
        "strict": True
        }
    }
    chat.terminal()


    