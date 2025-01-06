from api_ver import Base_llm

class DeepSeek(Base_llm):
    def __init__(self, api_key: str,
                 model: str = "deepseek-chat",
                 storage: str = "",
                 tools: list = [],
                 system_prompt: str = "",
                 limit: str = "128k",
                 proxy: dict = {
                     'http': 'http://127.0.0.1:7890',
                     'https': 'http://127.0.0.1:7890',
                 }
                 ):
        super().__init__(base_url="https://api.deepseek.com", api_key=api_key, model=model, storage=storage,
                         tools=tools, system_prompt=system_prompt, limit=limit, proxy=proxy)

    @Base_llm.result_appender  # type: ignore
    def list_models(self):
        url = f"{self.base_url}/models"
        response = self.client.get(url, proxies=self.proxy)
        if response.status_code == 200:
            result = response.json()
            return result.get("data")
        else:
            return response.status_code, response.json()

if __name__ == '__main__':
    api_key = "sk-63bcccdd316243aeac4e8cc5fcf5d8a1"
    tools = [
        {
            "type": "function",
            "function": {
                "name": "control_character",
                "description": "control the character's position, emotion, emoji, action,effect,and scaleup",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "position": {
                            "type": "string",
                            "description": "position of the character, choose from the following:1~5"
                        },
                        "emotion": {
                            "type": "string",
                            "description": "character's emotion, choose from the following:joy,sadness,anger,surprise,fear,disgust,normal,embarrassed"
                        },
                        "emoji": {
                            "type": "string",
                            "description": "display an emoji above a character's head or in a chat bubble,choose from the following:angry,bulb,chat,dot,exclaim,heart,music,question,respond,sad,shy,sigh,steam,surprise,sweat,tear,think,twinkle,upset,zzz"
                        },
                        "action": {
                            "type": "string",
                            "description": "character's action, choose from the following:sightly_down,fall_left,fall_right,jump,jump_more"
                        },
                        "effect": {
                            "type": "string",
                            "description": "character's effect, choose from the following:hide(use hide to hide the character),holography(use when chat through phone)"
                        },
                        "scaleup": {
                            "type": "string",
                            "description": "scale up the character when approaching the speaker, choose from the following:scaleup"
                        }
                    },
                    "required": ["position", "emotion"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "dir_walker",
                "description": "get file names in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir": {
                            "type": "string",
                            "description": "directory name, choose from the following:amusement, beach, bridge, building, busstation, cafe, camp, cathedral, citydowntown, countryside, elevator, food_stall, helicopter, home, hospital, hotel, indoorplaza, market",
                        }
                    },
                    "required": ["dir"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "bg_changer",
                "description": "chane the background image,use dir_walker to get the file names",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": f"directory/file,example:park/park.jpg",
                        }
                    },
                    "required": ["name"],
                },
            }
        }
    ]
    deepseek = DeepSeek(api_key=api_key,
                        limit="8k",
                        tools=tools,
                        proxy=None,# type: ignore
                        system_prompt="默认使用中文回复用户")  

    # result = deepseek.list_models()
    # print(result)
    result = deepseek.send({"role":"user","content": "你是deepseek什么版本"})
    print(result)
