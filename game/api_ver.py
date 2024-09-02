import os
from uuid import uuid4
import json
import requests


class ChatGLM:
    def __init__(self, api_key: str, model: str = "glm-4-flash", storage: str = "", tools: list = [], system_prompt: str = None):
        self.model = model
        self.client = requests.Session()
        self.client.headers.update({"Authorization": f"Bearer {api_key}"})
        self.history = []
        self.storage = storage
        self.tools = tools
        self.system_prompt = system_prompt
        if not self.is_valid_path(storage):
            raise ValueError("storage path is not valid")
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

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
                print(result)
                content = result["choices"][0]["message"]
                if content.get("content"):
                    self.history.append({"role": content.get(
                        "role"), "content": content.get("content")})
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


if __name__ == "__main__":
    api_key = "937041ab8a8913329177a408cc96fd4b.lC8CldSAjskjGtgS"
    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_train_info",
                "description": "根据用户提供的信息，查询对应的车次",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "departure": {
                            "type": "string",
                            "description": "出发城市或车站",
                        },
                        "destination": {
                            "type": "string",
                            "description": "目的地城市或车站",
                        },
                        "date": {
                            "type": "string",
                            "description": "要查询的车次日期",
                        },
                    },
                    "required": ["departure", "destination", "date"],
                },
            }
        }
    ]
    with open(os.path.join(r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\promot.txt"),"r",encoding="utf-8") as file:
        prompt=file.read()
    chatglm = ChatGLM(
        api_key, storage="C:\\Users\\water\\Desktop\\bot\\noa\\data\\chatglm",
        model="glm-4",tools=tools,system_prompt=prompt)

    messages = {
        "role": "user",
        "content": "你好"
    }

    reply = chatglm.send(messages=messages)
    print(reply)
    # id = chatglm.save()
    # print(id)
    # chatglm.load(id)
    # print(chatglm.history)
    # conversations = chatglm.get_conversations()
    # print(conversations)
    # chatglm.delete_conversation(id)
    # conversations = chatglm.get_conversations()
    # print(conversations)
