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
            action [Function(chat.clear_history),
                    Notify("历史记录已清除")]


screen tts_info:
    tag menu
    use game_menu(_("TTS"), scroll="viewport"):
        add DynamicDisplayable(show_gsv_output)

screen log:
    tag menu
    use game_menu(_("日志"), scroll="viewport"):
        add DynamicDisplayable(show_game_output)

screen uploaded_file():
    frame:
        background None
        # background Solid("#FFFFFF")
        pos (0,725)
        xsize 350
        ysize 355
        hbox:
            spacing 10
            button:
                add "images/icon/upload.png"
                action Function(uploader.add_file)
        viewport:
            pos(0,68)
            xsize 350
            ysize 287
            mousewheel True
            draggable True
            vbox:
                spacing 10
                for file in uploader.files:
                    hbox:
                        xsize 350
                        ysize 48
                        spacing 10
                        if uploader.get_file_type(file) == "image":
                            add "images/icon/image.png"
                        elif uploader.get_file_type(file) == "audio":
                            add "images/icon/audio.png"
                        $ filename=os.path.basename(file)
                        viewport:
                            # mousewheel "horizontal"
                            # draggable True
                            xsize 220
                            text "[filename]":
                                yoffset 3
                        button:
                            yoffset -11
                            xalign 1.0
                            add "images/icon/del.png"
                            action Function(uploader.remove_file,file)                         
