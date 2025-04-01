"""renpy
init 1 python:
"""
from io import BytesIO
from typing import Callable
from api_ver import GEMINI
import file_upload
import title_changer
import os
import json

def load_gsv_refer():
    refer_path = os.path.join(renpy.config.gamedir, "audio", "gsv") # type: ignore
    with open(os.path.join(refer_path, "config.json"), "r", encoding="utf-8") as file:
        config = json.load(file)
    return config
"""renpy
init 3 python:
"""
def load_agent_history(content:bytes):
    data=json.loads(content.decode("utf-8")) # type: ignore
    agent.store_history = data.copy() # type: ignore
    agent.chat_history =  data.copy() # type: ignore
    tokens = agent.tokenizer(agent.chat_history) # type: ignore
    if isinstance(tokens, int):
        if tokens >= agent.max_len: # type: ignore
            agent.limiter() # type: ignore

def load(conversation_id: str):
    conversation_id = chat.load(conversation_id,file_callbacks={"agent_history.json": load_agent_history}) # type: ignore
    change_title(conversation_id)
    renpy.store.conversation_id = conversation_id # type: ignore

def change_title(name: str):
    hwnd = title_changer.get_all_current_process_window_handles()
    # if len(hwnd)==1:
    #     title=title_changer.get_window_title(hwnd[0])
    #     title_changer.set_window_title(hwnd[0], name)
    # else:
    #     print("Error: Multiple windows are open.")
    #     title=title_changer.get_window_title(hwnd[0])
    #     title_changer.set_window_title(hwnd[0], name)
    title_changer.set_window_title(hwnd[0], name)


def play_tts_audio():
    if renpy.store.tts_audio: # type: ignore
        renpy.play(AudioData(renpy.store.tts_audio, "wav"), "voice") # type: ignore
    else:
        renpy.notify("暂无语音") # type: ignore


def save_tts_audio():
    if renpy.store.tts_audio: # type: ignore
        tts_dir = os.path.join(renpy.config.gamedir, "tts") # type: ignore
        with open(os.path.join(tts_dir, f"{renpy.store.tts_filename}.wav"), "wb") as file: # type: ignore
            file.write(renpy.store.tts_audio) # type: ignore
        renpy.notify("语音已保存") # type: ignore
    else:
        renpy.notify("暂无语音") # type: ignore


def save():
    agent_history=BytesIO()
    json_str=json.dumps(agent.store_history, ensure_ascii=False, indent=4) # type: ignore
    agent_history.write(json_str.encode("utf-8"))
    agent_history.seek(0)
    if renpy.store.conversation_id: # type: ignore
        renpy.store.conversation_id = chat.save(renpy.store.conversation_id,files={"agent_history.json": agent_history}) # type: ignore
    else:
        renpy.store.conversation_id = chat.save(files={"agent_history.json": agent_history}) # type: ignore

    change_title(renpy.store.conversation_id) # type: ignore
    renpy.notify("保存成功") # type: ignore

def show_gsv_output(st, at):
    if game_config.tts: # type: ignore
        if tts_terminal_output: # type: ignore
            text = []
            for info in tts_terminal_output: # type: ignore
                text.append(Text(info, substitute=False, # type: ignore
                            font="SourceHanSansCN-Bold.otf"))
            d = VBox(*text) # type: ignore
            return d, 1
        else:
            d = Text("tts启动中", font="SourceHanSansCN-Bold.otf") # type: ignore
            return d, 1
    else:
        d = Text("tts未开启", font="SourceHanSansCN-Bold.otf") # type: ignore
        return d, 1


def show_game_output(st, at):
    text = []
    for log in log_capture_handler.logs: # type: ignore
        log = log.replace("{", "{{")
        text.append(Text(log, substitute=False, # type: ignore
                    font="SourceHanSansCN-Bold.otf"))
    d = VBox(*text) # type: ignore
    return d, 1

class display_files():
    def __init__(self):
        self._files = []

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, new_files):
        if not isinstance(new_files, list):
            raise ValueError("files 必须是一个列表")

        old_files = self._files
        if old_files != new_files:
            self._files = new_files
            if new_files == []:
                pass
            else:
                renpy.redraw(uploaded_file, 0) # type: ignore

    def add_file(self):
        waiting = (file_upload.open_file_dialog_multiselect(
            title="请选择上传文件",
            file_types=[
                ["图片文件", "png", "jpeg", "jpg",
                 "webp", "heic", "heif"],
                ["音频文件", "wav", "mp3", "aiff",
                 "aac", "ogg", "flac"],
                ["所有文件", "png", "jpeg", "jpg", "webp", "heic", "heif",
                    "wav", "mp3", "aiff", "aac", "ogg", "flac"]
            ]
        )
        )
        for file in waiting:
            if file not in self.files:
                self.files.append(file)

    def remove_file(self, name: str):
        if name in self.files:
            self.files.remove(name)
        else:
            raise ValueError(f"{name} not exists")

    def get_file_type(self, file_path: str):
        format = os.path.splitext(file_path)[-1].lower()
        if format in GEMINI.image:
            return "image"
        elif format in GEMINI.audio:
            return "audio"
        else:
            return None
        
uploader = display_files()

