"""renpy
init 1 python:
"""
import os
from typing import  Union
from api_ver import GEMINI, MessageGenerator
from rag_client import RAG_Client
from datetime import datetime

rag_clinet = RAG_Client("http://127.0.0.1:20000")
rag_clinet.change_collection("Ushio_Noa")

message_generator = MessageGenerator(
    format="openai", file_format=GEMINI, ffmpeg_path="ffmpeg")

class Tools:
    def __init__(self,message_generator:MessageGenerator,rag_clinet:RAG_Client):
        self.function_args_data = {}
        self.map_data = {}
        self.message_generator = message_generator
        self.rag_client = rag_clinet

    def map_register(self, name: str, map_data: dict):
        self.map_data[name] = map_data

    def args_register(self, name: str, args: dict[str, type], required: list[str]):
        self.function_args_data[name] = {"args": args, "required": required}

    def args_check(self, name: str, args: dict)->Union[bool, str]:
        if name not in self.function_args_data:
            raise ValueError(f"function {name}'s arguments are not registered")
        
        missed_required = []
        type_error_args = []
        unexpected_args = []
        for r in self.function_args_data[name]["required"]:
            if r not in args:
                missed_required.append(r)
        for k, v in args.items():
            if k not in self.function_args_data[name]["args"]:
                unexpected_args.append(k)
            expected_type = self.function_args_data[name]["args"][k]
            if not isinstance(v, expected_type):
                type_error_args.append(f"{k}: expected {expected_type}, got {type(v)}")

        args_error = []
        if len(missed_required) > 0:
            args_error.append(f"missing required arguments: {missed_required}")
        if len(unexpected_args) > 0:
            args_error.append(f"unexpected arguments: {unexpected_args}")
        if len(type_error_args) > 0:
            args_error.append(f"argument type error: {type_error_args}")
        if len(args_error) > 0:
            error_message = ", ".join(args_error)
            return error_message
        else:
            return True

    def map_check(self, name: str, **kwargs)->Union[dict, str]:
        if name not in self.map_data:
            raise ValueError(f"Map data for '{name}' is not registered.")

        error_messages = []
        mapped_args = {}

        for arg_name, arg_value in kwargs.items():
            if arg_name not in self.map_data[name]:
                error_messages.append(
                    f"function '{name}' has no argument '{arg_name}'")
                continue

            valid_values = self.map_data[name].get(arg_name, {})
            if arg_value not in valid_values:
                error_messages.append(
                    f"Value '{arg_value}' for argument '{arg_name}' is not valid.")
            else:
                mapped_args[arg_name] = valid_values[arg_value]

        if error_messages:
            return ", ".join(error_messages)
        else:
            return mapped_args

    def dir_walker(self, dir: str):
        background_path = os.path.join(
            renpy.config.gamedir, "images/background")  # type: ignore
        path = os.path.join(background_path, dir)
        if not os.path.exists(path):
            return "directory not found"
        else:
            dir_names = []
            file_names = []
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_file(): 
                        if entry.name.endswith(".jpg"):
                            file_names.append(entry.name)
                    elif entry.is_dir():
                        dir_names.append(entry.name)
            return file_names

    def get_dirs(self, path: str = os.path.join(renpy.config.gamedir, "images/background")):  # type: ignore
        dir_names = []
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    dir_names.append(entry.name)
        return dir_names

    def control_character(self,
                          position: str,
                          emotion: str,
                          emoji: str = "",
                          action: str = "blank",
                          effect: str = "blank",
                          scaleup: str = "blank"):
        if emoji:
            mapped_args = self.map_check("control_character", position=position,
                                        emotion=emotion, emoji=emoji, action=action, effect=effect, scaleup=scaleup)
        else:
            mapped_args = self.map_check("control_character", position=position,
                                        emotion=emotion, action=action, effect=effect, scaleup=scaleup)

        if isinstance(mapped_args, str):
            return mapped_args

        if emoji:
            mapped_args.pop("emoji")
            renpy.show_screen(emoji, **mapped_args)  # type: ignore
            return "success"
        else:
            renpy.show_screen("noa_base", **mapped_args)  # type: ignore
            return "success"

    def bg_changer(self, name: str):
        if renpy.loadable("images/background/"+name):  # type: ignore
            image_name = name.split("/")[1][:-4]
            renpy.scene() # type: ignore
            renpy.show(image_name) # type: ignore
            renpy.with_statement(dissolve) # type: ignore
            renpy.store.current_background = image_name # type: ignore
            return "success"
        else:
            return "file not found"
    
    def store_memory(self, text: str, metadata: dict[str,str] = {}):
        self.rag_client.store(text, metadata)

    def query_memory(self, query_text: str, top_k: int = 1):
        return self.rag_client.query(query_text, top_k)
    
    def update_memory(self, id: str, text: str, metadata: dict[str,str] = {}):
        self.rag_client.update(id, text, metadata)

    def delete_memory(self, id: str):
        self.rag_client.delete(id)

    def get_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    

tool_collection = Tools(message_generator=message_generator,rag_clinet=rag_clinet)
tool_collection.args_register("dir_walker", {"dir": str}, ["dir"])
tool_collection.args_register("control_character", {"position": str, "emotion": str, "emoji": str,
                    "action": str, "effect": str, "scaleup": str}, ["position", "emotion"])
tool_collection.args_register("bg_changer", {"name": str}, ["name"])
tool_collection.args_register("end_of_tool_calls", {}, [])

tool_collection.map_register("control_character",
                    {
                        "position": {"1": "1",
                                    "2": "2",
                                    "3": "3",
                                    "4": "4",
                                    "5": "5"},
                        "emotion": {"joy": "joy",
                                    "sadness": "sadness",
                                    "anger": "anger",
                                    "surprise": "surprise",
                                    "fear": "fear",
                                    "disgust": "disgust",
                                    "embarrassed": "embarrassed",
                                    "normal": "normal"},
                        "emoji":  {"angry": "angry",
                                    "bulb": "bulb",
                                    "chat": "chat",
                                    "dot": "dot",
                                    "exclaim": "exclaim",
                                    "heart": "heart",
                                    "music": "music",
                                    "question": "question",
                                    "respond": "respond",
                                    "sad": "sad",
                                    "shy": "shy",
                                    "sigh": "sigh",
                                    "steam": "steam",
                                    "surprise": "surprise",
                                    "sweat": "sweat",
                                    "tear": "tear",
                                    "think": "think",
                                    "twinkle": "twinkle",
                                    "upset": "upset",
                                    "zzz": "zzz"},
                        "action": {"blank": blank,  # type: ignore
                                    "sightly_down": sightly_down,  # type: ignore
                                    "fall_left": fall_left,  # type: ignore
                                    "fall_right": fall_right,  # type: ignore
                                    "jump": jump,  # type: ignore
                                    "jump_more": jump_more,  # type: ignore
                                    "shake": shake,  # type: ignore
                                    "shake_more": shake_more},  # type: ignore
                        "effect": {"blank": blank,  # type: ignore
                                    "hide": "hide",
                                    "holography": "holography"},
                        "scaleup": {"blank": blank,  # type: ignore
                                    "scaleup": scaleup}  # type: ignore
                    })