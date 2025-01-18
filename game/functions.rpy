init 1 python:
    import sys

    def load(conversation_id:str):
        llm.event.put(("load",(conversation_id,)))
        while not llm.ready:
            time.sleep(0.1)
        llm.ready=False
        conversation_id=llm.result.get()
        change_title(conversation_id)
        renpy.store.conversation_id=conversation_id

    def change_title(name:str):
        hwnd=title_changer.get_all_current_process_window_handles()
        # if len(hwnd)==1:
        #     title=title_changer.get_window_title(hwnd[0])
        #     title_changer.set_window_title(hwnd[0], name)
        # else:
        #     print("Error: Multiple windows are open.")
        #     title=title_changer.get_window_title(hwnd[0])
        #     title_changer.set_window_title(hwnd[0], name)
        title_changer.set_window_title(hwnd[0], name)

    def play_tts_audio():
        if renpy.store.tts_audio:
            renpy.play(AudioData(renpy.store.tts_audio,"wav"),"voice")
        else:
            renpy.notify("暂无语音")

    def save_tts_audio():
        if renpy.store.tts_audio:
            tts_dir=os.path.join(renpy.config.gamedir,"tts")
            with open(os.path.join(tts_dir,f"{renpy.store.tts_filename}.wav"),"wb") as file:
                file.write(renpy.store.tts_audio)
            renpy.notify("语音已保存")
        else:
            renpy.notify("暂无语音")

    def save():
        if renpy.store.conversation_id:
            llm.event.put(("save",(renpy.store.conversation_id,)))
        else:
            llm.event.put(("save"))
        while not llm.ready:
            time.sleep(0.1)
        renpy.store.conversation_id=llm.result.get()
        change_title(renpy.store.conversation_id)
        renpy.notify("保存成功")

    def load_gsv_refer():
        refer_path=os.path.join(renpy.config.gamedir,"audio","gsv")
        with open(os.path.join(refer_path,"config.json"),"r",encoding="utf-8") as file:
            config=json.load(file)
        return config

    def show_gsv_output(st,at):
        if game_config.get("tts"):
            if tts_terminal_output:
                text = []
                for info in tts_terminal_output:
                    text.append(Text(info,substitute=False,font="SourceHanSansCN-Bold.otf"))
                d = VBox(*text)
                return d, 1
            else:
                d = Text("tts启动中",font="SourceHanSansCN-Bold.otf")
                return d, 1
        else:
            d = Text("tts未开启",font="SourceHanSansCN-Bold.otf")
            return d, 1
    def show_game_output(st,at):
        text = []
        for log in log_capture_handler.logs:
            log=log.replace("{","{{")
            text.append(Text(log,substitute=False,font="SourceHanSansCN-Bold.otf"))
        d = VBox(*text)
        return d, 1
    