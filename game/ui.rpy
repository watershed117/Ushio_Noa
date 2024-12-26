init 6 python:
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
        chatglm.event.put(("save"))
        while not chatglm.ready:
            time.sleep(0.1)
        chatglm.result.get()
        renpy.notify("保存成功")

screen main_ui:
    frame:
        background None
        xsize 1920
        ysize 50

        # left -> right

        #播放语音
        button:
            pos (10, 10)
            add "images/ui/audio1.png"
            action Function(play_tts_audio)

        #保存语音
        button:
            pos (70, 10)
            add "images/ui/save1.png"
            action Function(save_tts_audio)


        # right -> left
    
        #保存历史记录
        button:
            pos (1840,10)
            add "images/ui/save1.png"
            action Function(save)


        #刷新历史记录
        button:
            pos (1780,10)
            add "images/ui/refresh1.png"
            action [Function(chatglm.clear_history),
                    Notify("历史记录已清除")]
