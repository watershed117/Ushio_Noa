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
import time

def load_gsv_refer():
    refer_path = os.path.join(renpy.config.gamedir, "audio", "gsv") # type: ignore
    with open(os.path.join(refer_path, "config.json"), "r", encoding="utf-8") as file:
        config = json.load(file)
    return config
"""renpy
init 3 python:
"""
def load(conversation_id: str):
    conversation_id = chat.load(conversation_id) # type: ignore
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
    if renpy.store.conversation_id: # type: ignore
        renpy.store.conversation_id = chat.save(renpy.store.conversation_id) # type: ignore
    else:
        renpy.store.conversation_id = chat.save() # type: ignore

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

def polling_result(sleep_func:Callable[[float],None]=time.sleep,timeout:float=0.1):
    def polling(eid:str):
        result=eventloop.polling_result(eid=eid,sleep_func=sleep_func,timeout=timeout) # type: ignore
        if result.get("status")=="completed":
            return result.get("result")
        else:
            raise result.get("result")
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
                ja_data=json.loads(ja_data.get("content"))
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

tool_calls_handler=chat.handle_tool_calls(tool_calls_callback) # type: ignore
handler=chat.handle_message(handle_content,tool_calls_handler,callback=run_in_eventloop) # type: ignore