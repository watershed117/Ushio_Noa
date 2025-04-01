"""renpy
default preferences.gl_framerate = 30
init 0 python:
"""
from io import BytesIO
import logging
import time
from typing import Callable
from api_ver import GEMINI, Base_llm, MessageGenerator
from thread_pool import setup_logger,EventLoop
from audio_generator import Audio_generator
import os
import json

eventloop = EventLoop(num_workers=4,colored=False,log_level=logging.DEBUG,result_ttl=600, cleanup_interval=600)

class LogCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        if len(self.logs) > 1000:
            self.logs = self.logs[100:]
        self.logs.append(eventloop.logger.handlers[0].format(record))

root_logger = setup_logger("Global",colored=False)
root_logger.setLevel(logging.DEBUG)

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").propagate = False

log_capture_handler = LogCaptureHandler()
root_logger.addHandler(log_capture_handler)
eventloop.logger.addHandler(log_capture_handler)

class Config:
    def __init__(self, config_dict):
        self.chat_model = config_dict.get("chat_model")
        self.chat_base_url = config_dict.get("chat_base_url")
        self.chat_api_key = config_dict.get("chat_api_key")

        self.translator_model = config_dict.get("translator_model")
        self.translator_base_url = config_dict.get("translator_base_url")
        self.translator_api_key = config_dict.get("translator_api_key")

        self.agent_model = config_dict.get("agent_model")
        self.agent_base_url = config_dict.get("agent_base_url")
        self.agent_api_key = config_dict.get("agent_api_key")

        self.proxy = config_dict.get("proxy")

        self.tts = config_dict.get("tts", False)
        self.limit = config_dict.get("limit", "8k")

        self.gsv_bat_path = config_dict.get("gsv_bat_path")
        self.gsv_port = config_dict.get("gsv_port")
        
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

            "agent_model": "gemini-2.0-flash",
            "agent_base_url": "https://gemini.watershed.ip-ddns.com/v1",
            "agent_api_key": "",

            "proxy": {
                "http": None,
                "https": None
            },

            "tts": False,
            "limit": "8k",

            "gsv_bat_path":"",
            "gsv_port":9880
        }
        json.dump(data, file, indent=4, ensure_ascii=False)

with open(os.path.join(renpy.config.gamedir, "config.json"), "r", encoding="utf-8") as file:  # type: ignore
    game_config = Config(json.load(file))

"""renpy
init 2 python:
"""
def polling_result(sleep_func:Callable[[float],None]=time.sleep,timeout:float=0.1):
    def polling(eid:str):
        result=eventloop.polling_result(eid=eid,sleep_func=sleep_func,timeout=timeout) # type: ignore
        if result.get("status")=="completed":
            return result.get("result")
        else:
            raise result.get("result") # type: ignore
    return polling

poller=polling_result(sleep_func=renpy.pause,timeout=0.1) # type: ignore
background_poller=polling_result(sleep_func=time.sleep,timeout=0.1)

def run_in_eventloop(func: Callable, *args, raise_or_not: bool = False, **kwargs):
    """
    将函数添加到事件循环中执行，并通过 poller 获取结果。

    :param func: 要执行的函数
    :param args: 函数的位置参数
    :param raise_or_not: 是否在发生异常时重新抛出异常
    :param kwargs: 函数的关键字参数
    :return: 函数的执行结果
    """
    eid = eventloop.add_event(func, *args, **kwargs) # type: ignore
    try:
        return poller(eid)
    except Exception as e:
        root_logger.error( # type: ignore
            f"Failed to call {func.__name__} with args={args}, kwargs={kwargs}: {e}"
        )
        if raise_or_not:
            raise e

def translate(content:str):
    eid=eventloop.add_event(translator.send,{"role":"user","content":content}) # type: ignore
    reply=poller(eid)
    translator.clear_history() # type: ignore
    return reply

def handle_content(content: str):
    if content:
        if game_config.tts: # type: ignore
            try:
                ja_data=translate(content)
            except Exception as e:
                renpy.notify("翻译失败") # type: ignore
            try:
                ja_data=json.loads(ja_data.get("content")) # type: ignore
            except:
                renpy.notify("翻译json转换失败") # type: ignore
                root_logger.info(f"failed to load json: {ja_data}") # type: ignore
                ja_data=None
            if ja_data:
                ja=ja_data.get("text")
                emotion=ja_data.get("emotion")
                refer = tts_refer.get(emotion,tts_refer.get("normal")) # type: ignore
                refer_path=os.path.join(renpy.config.gamedir, "audio", "gsv",refer[0]) # type: ignore
                refer_text=refer[1]
                refer_data={"refer_wav_path": refer_path, "prompt_text": refer_text, "prompt_language": "all_ja"}
                
                # 合成语音
                eid=eventloop.add_event(tts.gen, {"text": ja, "language": "ja", "refer_data": refer_data}) # type: ignore
                try:
                    audio=poller(eid)
                except Exception as e:
                    renpy.notify("语音合成失败") # type: ignore
                    audio=None

                if audio:
                    if isinstance(audio,BytesIO):
                        renpy.store.tts_audio=audio.getvalue() # type: ignore
                        renpy.store.tts_filename=content[:10] # type: ignore
                        renpy.play(AudioData(renpy.store.tts_audio,"wav")) # type: ignore
                    else:
                        renpy.notify("合成语音失败") # type: ignore

    renpy.say(noa, content) # type: ignore

def tool_calls_callback(func:Callable,**kwargs):
    if func.__name__ in renpy.store.run_in_main_context: # type: ignore
        root_logger.info(f"calling {func.__name__} in main context") # type: ignore
        return func(**kwargs)
    else:
        eid=eventloop.add_event(func,**kwargs) # type: ignore
        try:
            root_logger.info(f"calling {func.__name__} in background") # type: ignore
            return background_poller(eid)
        except Exception as e:
            root_logger.error(f"failed to call {func.__name__}: {e}") # type: ignore

class Chat_Tool_Collection:
    def __init__(self,agent:Base_llm,message_generator:MessageGenerator) -> None:
        self.agent = agent
        self.message_generator = message_generator
        self.tool_calls_handler=self.agent.handle_tool_calls(self.tool_calls_callback) # type: ignore

    def tool_calls_callback(self,func:Callable,**kwargs):
        if func.__name__ in renpy.store.run_in_main_context: # type: ignore
            root_logger.info(f"agent calling {func.__name__} in main context") # type: ignore
            root_logger.debug(f"agent calling {func.__name__} with args={kwargs}") 
            return func(**kwargs)
        else:
            eid=eventloop.add_event(func,**kwargs) # type: ignore
            try:
                root_logger.info(f"agent calling {func.__name__} in background")
                root_logger.debug(f"agent calling {func.__name__} with args={kwargs}") 
                return background_poller(eid)
            except Exception as e:
                root_logger.error(f"agent failed to call {func.__name__}: {e}")

    def agent_commander(self,message: str, files: list[str] = []):
        reply = self.agent.send(self.message_generator.gen_user_msg(message, files))
        while True:
            if reply.get("tool_calls"):
                tool_messages = self.tool_calls_handler(reply.get("tool_calls"))
                reply = self.agent.send(tool_messages)
                if not reply.get("tool_calls") and reply.get("content"):
                    root_logger.info(f"agent reply: {reply.get('content')}") 
                    return reply.get("content")
            elif reply.get("content"):
                root_logger.info(f"agent reply: {reply.get('content')}") 
                return reply.get("content")
            
    def clear_history(self):
        self.agent.clear_history()
        return "success"

dirs = tool_collection.get_dirs(os.path.join(  # type: ignore
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
                        "description": "position of the character",
                        "enum":["1","2","3","4","5"]
                    },
                    "emotion": {
                        "type": "string",
                        "description": "display character's face with emotion",
                        "enum":["joy","sadness","anger","surprise","fear","disgust","normal","embarrassed"]
                    },
                    "emoji": {
                        "type": "string",
                        "description": "display an emoji above a character's head or in a chat bubble",
                        "enum":["angry","bulb","chat","dot","exclaim","heart","music","question","respond","sad","shy","sigh","steam","surprise","sweat","tear","think","twinkle","upset","zzz"]
                    },
                    "action": {
                        "type": "string",
                        "description": "character's action",
                        "enum":["sightly_down","fall_left","fall_right","jump","jump_more"]
                    },
                    "effect": {
                        "type": "string",
                        "description": "character's effect,use hide to hide the character,use holography when chat through phone",
                        "enum":["hide","holography"]
                    },
                    "scaleup": {
                        "type": "string",
                        "description": "scale up the character when approaching the speaker",
                        "enum":["scaleup"]
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
                        "description": "directory name",
                        "enum": dirs
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
            "name": "store_memory",
            "description": "store text and metadata in RAG system,return the id of the text",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "text to store"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "metadata to store,key-value pairs",
                        "additionalProperties": {
                            "type": "string"
                        }
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_memory",
            "description": "query RAG system for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_text": {
                        "type": "string",
                        "description": "text to query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "number of results to return",
                        "default": 1
                    }
                },
                "required": ["query_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_memory",
            "description": "update data in RAG system",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID of the text to update"
                    },
                    "text": {
                        "type": "string",
                        "description": "text to update"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "metadata to update,key-value pairs",
                        "additionalProperties": {
                            "type": "string"
                        }
                    }
                },
                "required": ["id", "text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete",
            "description": "delete data in RAG system",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID of the text to delete"
                    }
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "get current time"
            }
    }
]

chat_tools = [
    {
        "type": "function",
        "function": {
            "name": "agent_commander",
            "description": "send command to agent to call functions,this agent is a llm can process image and audio",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Natural Language message to send to agent, don't include file paths in message",
                    },
                    "files":{
                        "type": "array",
                        "description": "full file paths",
                        "items": {
                            "type": "string"
                        },
                    }
                },
                "required": ["message"],
            },
        }
    }
]

with open(os.path.join(renpy.config.gamedir,"prompts", "promot.txt"), "r", encoding="utf-8") as file:  # type: ignore
    complex_prompt = file.read()

# with open(os.path.join(renpy.config.gamedir,"prompts", "tmp.txt"), "r", encoding="utf-8") as file:  # type: ignore
#     complex_prompt = file.read()

with open(os.path.join(renpy.config.gamedir, "prompts","translator.txt"), "r", encoding="utf-8") as file:  # type: ignore
    translator_prompt = file.read()

with open(os.path.join(renpy.config.gamedir, "prompts","agent_prompt.txt"), "r", encoding="utf-8") as file:  # type: ignore
    agent_prompt = file.read()

agent = Base_llm(api_key=game_config.agent_api_key,
                base_url=game_config.agent_base_url,
                model=game_config.agent_model,
                proxy=game_config.proxy,
                limit=game_config.limit,
                system_prompt=agent_prompt,
                tools=tools,
                tool_collection=tool_collection) # type: ignore

chat_tool_collection = Chat_Tool_Collection(agent=agent,message_generator=message_generator) # type: ignore

chat = Base_llm(api_key=game_config.chat_api_key,
                base_url=game_config.chat_base_url,
                storage=os.path.join(renpy.config.gamedir, "history"), # type: ignore
                model=game_config.chat_model,
                proxy=game_config.proxy,
                system_prompt=complex_prompt,
                tools=chat_tools,
                tool_collection=chat_tool_collection) # type: ignore

tool_calls_handler=chat.handle_tool_calls(tool_calls_callback) # type: ignore
handler=chat.handle_message(handle_content,tool_calls_handler,callback=run_in_eventloop) # type: ignore

translator = Base_llm(api_key=game_config.translator_api_key,
                    base_url=game_config.translator_base_url,
                    model=game_config.translator_model,
                    proxy=game_config.proxy,
                    system_prompt=translator_prompt)

renpy.invoke_in_thread(eventloop.start)  # type: ignore

tts_terminal_output = []
if game_config.tts:
    import subprocess

    def read_output(stream):
        global tts_terminal_output
        for line in stream:
            if len(tts_terminal_output) > 1000:
                tts_terminal_output = tts_terminal_output[-1000:]
            tts_terminal_output.append(line.decode("gbk").strip())

    process = subprocess.Popen(
        game_config.gsv_bat_path,
        cwd=os.path.dirname(game_config.gsv_bat_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
        shell=True,
        creationflags=subprocess.CREATE_NO_WINDOW
    )

    renpy.invoke_in_thread(read_output, process.stdout)  # type: ignore
    renpy.invoke_in_thread(read_output, process.stderr)  # type: ignore

    tts_refer = load_gsv_refer()  # type: ignore
    tts = Audio_generator(port=game_config.gsv_port)