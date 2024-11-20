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

        if not self.is_valid_path(storage):
            raise ValueError("storage path is not valid")
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})
            self.history_storage.append(
                {"role": "system", "content": system_prompt})

    def is_valid_path(self, path_str: str):
        try:
            os.path.exists(path_str)
            return True
        except Exception:
            return False

    def get_creation_time(self, file_path):
        return os.path.getctime(file_path)

    def send(self, messages: dict):
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        with self.client as client:
            self.history.append(messages)
            playload = {"model": self.model, "messages": self.history}
            if self.tools:
                playload.update({"tools": self.tools})
            response = client.post(url, json=playload)
            if response.status_code == 200:
                result = response.json()
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

    def save(self):
        id = str(uuid4())
        print(os.path.join(self.storage, f"{id}.json"))
        with open(os.path.join(self.storage, f"{id}.json"), "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)
        return id

    def load(self, id: str):
        with open(os.path.join(self.storage, f"{id}.json"), "r", encoding="utf-8") as f:
            self.history = json.load(f)

    def sort_files(self, folder_path):
        # 获取文件夹下的所有文件
        files = [os.path.join(folder_path, f) for f in os.listdir(
            folder_path) if f.endswith('.json')]

        # 根据创建时间排序
        files.sort(key=self.get_creation_time, reverse=True)
        return files

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

    def delete_conversation(self, id: str):
        file_path = os.path.join(self.storage, f"{id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return False

    def tokenizer(self, data: list[dict[str, str]]) -> int | tuple:
        url = "https://open.bigmodel.cn/api/paas/v4/tokenizer"
        with self.client as client:
            response = client.post(url, json=data)
            if response.status_code == 200:
                result = response.json()
                return result["usage"].get("prompt_tokens")
            else:
                return response.status_code, response.json()

    def limiter(self):
        self.history = self.history[:1] + self.history[3:]
        tokens = self.tokenizer(self.history)
        if isinstance(tokens, int):
            if tokens >= self.max_len:
                self.limiter()

    def call_method(self, method_name: str, *args, **kwargs):
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                print( f"call method {method_name}")
                return method(*args, **kwargs)
            else:
                print(f"{method_name} not callable")
                return None
        else:
            print(f"{method_name} not found")
            return None

    def run(self):
        while True:
            event = self.event.get()
            if not event:
                continue
            if isinstance(event, str):
                method_name = event
                result = self.call_method(method_name)
                print(result)
                continue
            elif isinstance(event, tuple):
                method_name = event[0]
                if len(event) == 1:
                    result = self.call_method(method_name)
                    print(result)
                    continue
                elif len(event) == 2:
                    if isinstance(event[1], tuple):
                        args = event[1]
                        result = self.call_method(method_name, *args)
                        print(result)
                    elif isinstance(event[1], dict):
                        kwargs = event[1]
                        result = self.call_method(method_name, **kwargs)
                        print(result)
                    else:
                        continue
                elif len(event) == 3:
                    args = event[1]
                    kwargs = event[2]
                    result = self.call_method(method_name, *args, **kwargs)
                    print(result)
                else:
                    continue
            else:
                continue



if __name__ == "__main__":
    api_key = "3c82d2b319fc300ad8ea63a3d90f7350.Rgje8i6T9jDOetD4"
    tools = [
        {
            "type": "function",
                    "function": {
                        "name": "control_character",
                        "description": "控制角色的立绘，表情，动作，特效",
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

    # with open(os.path.join(r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\promot.txt"), "r", encoding="utf-8") as file:
    #     complex_prompt = file.read()
    with open(os.path.join(r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\test.txt"), "r", encoding="utf-8") as file:
        complex_prompt = file.read()

    # chatglm = ChatGLM(
    #     api_key, storage=r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\history",
    #     model="glm-4-plus", system_prompt=complex_prompt, tools=tools)
    chatglm = ChatGLM(
        api_key, storage=r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\history",
        model="glm-4-flash", system_prompt="", limit="8k")
    # while True:
    #     messages = {
    #         "role": "user",
    #         "content": input("请输入：")
    #     }
    #     reply = chatglm.send(messages=messages)
    #     print(reply)
    # if reply.get("tool_calls"):
    #     reply = chatglm.send(
    #         messages={"role": "tool", "content": "[{'control_character': 'success'}]", "tool_call_id": reply.get("tool_calls")[0].get("id")})
    #     print(reply)

    import threading
    t = threading.Thread(target=chatglm.run)
    t.start()
    chatglm.event.put(("send",({"role": "user", "content": "你好"},)))
    chatglm.event.put(("send",{"messages":{"role": "user", "content": "你好"}}))

