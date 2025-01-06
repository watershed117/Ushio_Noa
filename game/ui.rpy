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
            action [Function(llm.clear_history),
                    Notify("历史记录已清除")]


screen tts_info:
    tag menu
    use game_menu(_("TTS"), scroll="viewport"):
        add DynamicDisplayable(show_gsv_output)

screen log:
    tag menu
    use game_menu(_("日志"), scroll="viewport"):
        add DynamicDisplayable(show_game_output)


