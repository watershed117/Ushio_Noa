"""renpy
init 0 python:
"""
import logging
from api_ver import Base_llm, Gemini
from event_loop import EventLoop, setup_logging
from audio_generator import Audio_generator
import os
import json


class LogCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        if len(self.logs) > 1000:
            self.logs = self.logs[100:]
        self.logs.append(self.format(record))


root_logger = setup_logging("root", False)
root_logger.setLevel(logging.DEBUG)
log_capture_handler = LogCaptureHandler()
log_capture_handler.setLevel(logging.DEBUG)
root_logger.addHandler(log_capture_handler)


class Config:
    def __init__(self, config_dict):
        self.chat_model = config_dict.get("chat_model")
        self.chat_base_url = config_dict.get("chat_base_url")
        self.chat_api_key = config_dict.get("chat_api_key")

        self.translator_model = config_dict.get("translator_model")
        self.translator_base_url = config_dict.get("translator_base_url")
        self.translator_api_key = config_dict.get("translator_api_key")

        self.multimodal_model = config_dict.get("multimodal_model")
        self.multimodal_base_url = config_dict.get("multimodal_base_url")
        self.multimodal_api_key = config_dict.get("multimodal_api_key")

        self.proxy = config_dict.get("proxy")

        self.tts = config_dict.get("tts", False)
        self.limit = config_dict.get("limit", "8k")
        self.siliconflow_api_key = config_dict.get("siliconflow_api_key")


if not os.path.exists(os.path.join(renpy.config.gamedir, "history")):  # type: ignore
    os.makedirs(os.path.join(renpy.config.gamedir, "history"))  # type: ignore
if not os.path.exists(os.path.join(renpy.config.gamedir, "config.json")):  # type: ignore
    with open(os.path.join(renpy.config.gamedir, "config.json"), "w", encoding="utf-8") as file:  # type: ignore
        data = {
            "chat_model": "deepseek-chat",
            "chat_base_url": "https://api.deepseek.com",
            "chat_api_key": "",

            "translator_model": "glm-4-flash",
            "translator_base_url": "https://open.bigmodel.cn/api/paas/v4",
            "translator_api_key": "",

            "multimodal_model": "gemini-1.5-flash",
            "multimodal_base_url": "https://gemini.watershed.ip-ddns.com/v1",
            "multimodal_api_key": "",

            "proxy": {
                "http": None,
                "https": None
            },

            "tts": False,
            "limit": "8k",
        }
        json.dump(data, file, indent=4, ensure_ascii=False)

with open(os.path.join(renpy.config.gamedir, "config.json"), "r", encoding="utf-8") as file:  # type: ignore
    game_config = Config(json.load(file))

"""renpy
init 2 python:
"""
dirs = tools_caller.get_dirs(os.path.join(  # type: ignore
    renpy.config.gamedir, "images/background"))  # type: ignore
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
                        "description": f"directory name, choose from the following:{dirs}",
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
            "description": "chane the background image,use api 'dir_walker' to get the file names",
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
    },
    {
        "type": "function",
        "function": {
            "name": "chat_with_multimodal",
            "description": "Interacts with a multimodal language model to get information of file",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "text send to the multimodal language model",
                    },
                    "files": {
                        "type": "array",
                        "description": "full file paths",
                    }
                },
                "required": ["message", "files"],
            },
        }
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "clear_multimodal_history",
    #         "description": "clear the multimodal language model's history",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {}
    #         }
    #     }
    # },
]

with open(os.path.join(renpy.config.gamedir, "promot.txt"), "r", encoding="utf-8") as file:  # type: ignore
    complex_prompt = file.read()

with open(os.path.join(renpy.config.gamedir, "translator.txt"), "r", encoding="utf-8") as file:  # type: ignore
    translator_prompt = file.read()

chat = Base_llm(api_key=game_config.chat_api_key,
                base_url=game_config.chat_base_url,
                storage=os.path.join(renpy.config.gamedir, "history"), # type: ignore
                model=game_config.chat_model,
                proxy=game_config.proxy,
                system_prompt=complex_prompt,
                tools=tools)

# chat = Base_llm(api_key="6b98385d296d8687ec15b54faa43a01c.43RrndejVMU5KmJE",
#                 base_url="https://open.bigmodel.cn/api/paas/v4",
#                 storage=os.path.join(renpy.config.gamedir,  # type: ignore
#                                      "history"),
#                 model="glm-4-flash",
#                 proxy=game_config.proxy,
#                 system_prompt=complex_prompt,
#                 tools=tools)

# chat = Base_llm(api_key="sk-bltyfqycpshmbeferivmixvhqahjsunjofzbckflnqxpksoe",
#                 base_url="https://api.siliconflow.cn/v1",
#                 storage=os.path.join(renpy.config.gamedir, "history"), # type: ignore
#                 model="deepseek-ai/DeepSeek-V3",
#                 proxy=game_config.proxy,
#                 system_prompt=complex_prompt,
#                 tools=tools)

translator = Base_llm(api_key=game_config.translator_api_key,
                      base_url=game_config.translator_base_url,
                      model=game_config.translator_model,
                      proxy=game_config.proxy,
                      system_prompt=translator_prompt)

renpy.invoke_in_thread(eventloop.run)  # type: ignore

tts_terminal_output = []
if game_config.tts:
    import subprocess

    def read_output(stream):
        global tts_terminal_output
        for line in stream:
            if len(tts_terminal_output) > 1000:
                tts_terminal_output = tts_terminal_output[-1000:]
            tts_terminal_output.append(line.decode("gbk").strip())

    # bat_file_path = os.path.join(renpy.config.gamedir,"GPT-SoVITS-v2-240821","GPT-SoVITS-v2-240821","api.bat")
    bat_file_path = r"D:\GPT-SoVITS-v2-240821\GPT-SoVITS-v2-240821\api.bat"

    process = subprocess.Popen(
        bat_file_path,
        # cwd=os.path.join(renpy.config.gamedir,"GPT-SoVITS-v2-240821","GPT-SoVITS-v2-240821"),
        cwd=r"D:\GPT-SoVITS-v2-240821\GPT-SoVITS-v2-240821",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        shell=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    renpy.invoke_in_thread(read_output, process.stdout)  # type: ignore
    renpy.invoke_in_thread(read_output, process.stderr)  # type: ignore

    tts_refer = load_gsv_refer()  # type: ignore
    tts = Audio_generator()
