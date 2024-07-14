import requests
import json
class Chatglm():
    def __init__(self,
                 token: str,
                 refresh_token:str,
                 acw_tc:str,
                 assistant_id:str,
                 timeout: int = 60,
                 conversation_id:str="",
                 proxy:str=None) -> None:

        self.token=token
        self.acw_tc=acw_tc
        self.refresh_token=refresh_token
        self.timeout=timeout
        self.proxy=proxy

        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Cookie': f'acw_tc={acw_tc}',
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }
        self.client = requests.Session()
        self.client.headers.update(self.headers)
        self.assistant_id=assistant_id
        self.conversation_id=conversation_id
    def send(self,message:str,conversation_id:str=""):
        payload = {
            "assistant_id": self.assistant_id,
            "conversation_id": conversation_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            ],
            "meta_data": {
                "is_test": False,
                "input_question_type": "xxxx",
                "channel": "",
                "draft_id": ""
            }
        }
        with self.client.post(url="https://chatglm.cn/chatglm/backend-api/assistant/stream", json=payload,stream=True,timeout=self.timeout,proxies={"all":self.proxy}) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                line=line.decode('utf-8')
                if line.startswith("data:"):
                    data = json.loads(line[6:])
                    # print(data)
                    conversation_id = data.get("conversation_id")
                    parts = data.get("parts")
                    if parts:
                        # model=parts[0].get("model")
                        # logic_id=parts[0].get("logic_id")
                        content = parts[0].get("content")
                        if content:
                            text = content[0].get("text")
            # "logic_id":logic_id,"model":model}
            self.conversation_id=conversation_id
            return {"conversation_id": conversation_id, "text": text}

    def delete(self,conversation_id:str):
        url = "https://chatglm.cn/chatglm/backend-api/assistant/conversation/delete"
        playload = {"assistant_id": self.assistant_id,
                    "conversation_id": conversation_id}
        response=self.client.post(url=url,json=playload,timeout=self.timeout,proxies={"all":self.proxy})
        response.raise_for_status()
    def recommand(self,conversation_id:str):
        url = f"https://chatglm.cn/chatglm/backend-api/v1/conversation/recommendation/list?conversation_id={conversation_id}"
        response=self.client.get(url=url,timeout=self.timeout,proxies={"all":self.proxy}) 
        response.raise_for_status()
        return response.json().get("result").get("list")
    def get_conversations(self,page:int=1,page_size:int=25):
        url=f"https://chatglm.cn/chatglm/backend-api/assistant/conversation/list?assistant_id={self.assistant_id}&page={page}&page_size={page_size}"
        response=self.client.get(url=url,timeout=self.timeout,proxies={"all":self.proxy})
        response.raise_for_status()
        conversation_list=response.json().get("result").get("conversation_list")
        if conversation_list:
            tmp_list=[]
            for conversation in conversation_list:
                assistant_id=conversation.get("assistant_id")
                conversation_id=conversation.get("id")
                title=conversation.get("title")
                tmp_list.append({"assistant_id":assistant_id,"conversation_id":conversation_id,"title":title})
            return tmp_list,response.json().get("result").get("has_more") or False
    def get_history(self,conversation_id:str):
        url=f"https://chatglm.cn/chatglm/backend-api/assistant/conversation?assistant_id={self.assistant_id}&conversation_id={conversation_id}"
        response=self.client.get(url=url,timeout=self.timeout,proxies={"all":self.proxy})
        response.raise_for_status()
        messages=response.json().get("result").get("messages")
        tmp_list=[]
        for message in messages:
            input=message.get("input")
            text=input.get("content")[0].get("text")
            role=input.get("role")
            tmp_list.append({role:text})
            output=message.get("output")
            text=output.get("parts")[0].get("content")[0].get("text")
            role=output.get("role")
            tmp_list.append({role:text})
        return tmp_list
    def refresh(self,refresh_token:str)->bool:
        url="https://chatglm.cn/chatglm/backend-api/v1/user/refresh"
        self.client.headers.update({'Authorization': f'Bearer {refresh_token}'})
        response=self.client.post(url=url,timeout=self.timeout,proxies={"all":self.proxy})
        if response.status_code==200:
            self.token=response.json().get("result").get("accessToken")
            self.acw_tc=response.cookies.get("acw_tc")
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'Cookie': f'acw_tc={self.acw_tc}',
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            }
            self.client.headers.update(self.headers)
            return True
        else:
            return False