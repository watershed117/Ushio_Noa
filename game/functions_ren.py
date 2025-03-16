"""renpy
init 1 python:
"""
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

# def show_uploaded_files(st,at):
#     for file in renpy.store.files:


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

def handle_tool_calls(reply: dict):
    """
    处理回复中的 tool 调用。
    """
    # 并发调用 tool
    for tool in reply.get("tool_calls", []):# type: ignore
        function=tool.get("function")
        tool_id=tool.get("id")
        root_logger.info(f"调用tool:{function}")# type: ignore
        tools_caller.caller(function,tool_id)# type: ignore
    # 等待所有 tool 调用完成并收集结果
    messages = []

    while tools_caller.tool_result.empty(): # type: ignore
        renpy.pause(0.1)
    data=tools_caller.tool_result.get()
    payload = {
        "role": "tool",
        "content": str(data.get("result")).replace("\\'", "'"),
        "tool_call_id": data.get("tool_call_id")
    }
    messages.append(payload)
    # 将 tool 结果发送回 chat.send
    eid = eventloop.add_event(chat.send, messages)
    # 等待消息发送完成
    while eventloop.event_results[eid]["status"] == "pending": # type: ignore
        renpy.pause(0.1) 
    if eventloop.event_results[eid]["status"] == "completed":
        reply=eventloop.get_event_result(eid).get("result")
        return reply
    else:
        error=eventloop.get_event_result(eid)
        raise error.get("result")


def handle_content(reply: dict):
    if reply.get("content"):
        tts_ready=False
        if game_config.tts: # type: ignore
            # 翻译为日语
            eid=eventloop.add_event(translator.send,{"role":"user","content":reply.get("content")}) # type: ignore
            renpy.notify("翻译中") # type: ignore
            while eventloop.event_results[eid]["status"] == "pending": # type: ignore
                renpy.pause(0.1) # type: ignore
            if eventloop.event_results[eid]["status"] == "completed":
                ja_reply=eventloop.get_event_result(eid).get("result")
            else:
                error=eventloop.get_event_result(eid)
                raise error.get("result")
            translator.clear_history()
            renpy.notify("翻译完成")

            # 加载json格式
            try:
                ja_reply=json.loads(ja_reply.get("content"))
                ja_load=True
            except:
                root_logger.info("failed to load json")
                ja_load=False

            # 获取参考音频
            if ja_load:
                ja=ja_reply.get("text")
                emotion=ja_reply.get("emotion")
                root_logger.info(f"ja:{ja}")
                root_logger.info(f"emotion:{emotion}")
                refer = tts_refer.get(emotion)
                if not refer:
                    refer = tts_refer.get("normal")
                refer_path=os.path.join(renpy.config.gamedir, "audio", "gsv",refer[0])
                refer_text=refer[1]
                refer_data={"refer_wav_path": refer_path, "prompt_text": refer_text, "prompt_language": "all_ja"}
                
                # 合成语音
                eid=eventloop.add_event(tts.gen, {"text": ja, "language": "ja", "refer_data": refer_data})
                renpy.notify("合成语音中")
                while eventloop.event_results[eid]["status"] == "pending":
                    renpy.pause(0.1)
                if eventloop.event_results[eid]["status"] == "completed":
                    audio=eventloop.get_event_result(eid).get("result")
                else:
                    error=eventloop.get_event_result(eid)
                    raise error.get("result")

                # 判断是否成功
                if isinstance(audio,BytesIO):
                    renpy.store.tts_audio=audio.getvalue()
                    tts_ready=True
                    renpy.notify("合成语音成功")
                else:
                    renpy.notify("合成语音失败")
                    root_logger.info(f"语音合成失败: {audio}")

            else:
                renpy.notify("翻译格式转换失败")
                root_logger.info(f"failed to load json: {ja_reply}")

        # 播放音频+显示消息
        if tts_ready:
            renpy.play(AudioData(renpy.store.tts_audio,"wav"))
            renpy.store.tts_filename=reply.get("content")[:10]
        renpy.say(noa,reply.get("content"))
        # renpy.invoke_in_main_thread(renpy.say,noa,reply.get("content"))

def handle_reply(reply: dict):
    """
    处理来自聊天系统的回复，包括 tool 调用和内容。
    """
    tmp=None
    # 1. Tool 调用处理
    if reply.get("tool_calls"):
        tmp=handle_tool_calls(reply) # 不直接返回，通过queue传递结果
    # 2. 内容处理
    if reply.get("content"):
        handle_content(reply) # 处理内容
    if tmp:
        handle_reply(tmp) # 处理子回复

    renpy.store.reply_handle_status = True # 确保主循环能继续
