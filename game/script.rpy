init 2 python:
    import time
    import queue
    from io import BytesIO    

init 5 python:
    config.keymap['rollback'].remove('anyrepeat_K_PAGEUP')
    config.keymap['rollback'].remove('anyrepeat_KP_PAGEUP')
    config.keymap['rollback'].remove('K_AC_BACK')
    config.keymap['rollback'].remove('mousedown_4')

    if game_config.tts:
        while  True:
            if "INFO:     Uvicorn running on http://127.0.0.1:9880 (Press CTRL+C to quit)" in tts_terminal_output:
                break
            time.sleep(0.1)
        config.quit_callbacks.append(tts.exit)

screen entry():
    python:
        eid=eventloop.add_event(chat.get_conversations)
        while eventloop.event_results[eid]["status"] == "pending":
            time.sleep(0.1)
        if eventloop.event_results[eid]["status"] == "completed":
            conversation_list=eventloop.get_event_result(eid).get("result")
        else:
            error=eventloop.get_event_result(eid)
            raise error.get("result")

    add "images/ui/ui.png"
    viewport:
        pos(1101,162)
        xsize 800
        ysize 854
        mousewheel True
        scrollbars("vertical")
        add "images/ui/frame.png":
            pos (0,0)
        text "{size=32}0{/size}":
            pos(30, 25)
        text "{size=32}新建会话{/size}":
            pos(108, 25)
        button:
            pos(582, 8)
            add "images/ui/button.png"
            action [Function(chat.clear_history),
                    SetVariable("new_conversation",True),
                    Jump("main")]
        if conversation_list:
            $ conversation_number=len(conversation_list)
            #frame
            vbox:
                pos(0,144)
                spacing 52
                for n in range(0,conversation_number):
                    add "images/ui/frame.png"
            #text
            vbox:
                pos(30, 169)
                spacing 104
                for n in range(0,conversation_number):
                    python:
                        title=conversation_list[n].get("title")
                        if len(title)>10:
                            title=title[:10].replace("\n", "")
                    hbox:
                        spacing 60
                        text "{size=32}[n+1]{/size}" 
                        text "{size=32}[title]{/size}" 
            #button
            vbox:
                pos(582,150)
                spacing 66
                for n in range(0,conversation_number):
                    button:
                        add "images/ui/button.png"
                        action [Function(load,conversation_list[n].get("id")),
                                Jump("main")]
          
label start:
    stop music fadeout 1.0
    call screen entry()
    return

# default upload=True
# default files=[]
# label start:
#     stop music fadeout 1.0
#     scene expression "images/background/office/mainoffice.jpg"
#     $ text=renpy.input("sensei")
#     noa "[text]"
#     noa "[uploader.files]"
#     $ uploader.files=[]
#     pause
#     return

label ready:
    show ready with CropMove(1.0, "wipedown")
    hide loading
    return

label main:
    hide screen entry
    show loading
    python:
        if not new_conversation:
            latest_message=chat.get_latest_message(chat.chat_history)
            control_recall=chat.latest_tool_recall(chat.chat_history,"control_character")
            bg_recall=chat.latest_tool_recall(chat.chat_history,"bg_changer")

            recall_data=queue.Queue()
            if control_recall:
                renpy.store.recall_data.put(control_recall[0])
            if bg_recall:
                renpy.store.recall_data.put(bg_recall[0])

            if recall_data.empty():
                recall_statue=False
            else:
                recall_statue=True

            renpy.call("ready")

        else:
            recall_statue=False
            
    if not new_conversation:
        if recall_statue:
            while not recall_data.empty():
                python:
                    root_logger.info("recalling...")
                    data=recall_data.get()
                    if data.get("name") in tool_call_counts:
                        renpy.store.tool_call_counts[data.get("name")]+=1
                    tools_caller.caller(data)
                    
    python:
        if recall_statue:
            root_logger.info(renpy.store.tool_call_counts)
            if renpy.store.tool_call_counts.get("control_character")==0:
                renpy.show_screen("noa_base","3","joy")
            if renpy.store.tool_call_counts.get("bg_changer")==0:
                renpy.call("bg_changer", "office/mainoffice.jpg")

    python:
        if not new_conversation:
            if latest_message:
                renpy.say(noa,latest_message)

    python:
        if new_conversation:
            new_conversation=False
            renpy.show_screen("noa_base","3","joy")
            renpy.call("bg_changer", "office/mainoffice.jpg")

    hide ready
    show screen main_ui
    jump main_loop
    return

label message_processor(reply):
    python:
        root_logger.info(reply)
        tool_statue=False
        tool_data=queue.Queue()
        result_statue=False
        renpy.store.tool_result=queue.Queue()
        tool_id=queue.Queue()
        tts_ready=False
        root_logger.info("开始处理消息")

    python:
        if reply.get("tool_calls"):
            root_logger.info("获取tool参数")
            for tool in reply.get("tool_calls"):
                tool_id.put(tool.get("id"))
                function=tool.get("function")
                tool_data.put(function)
            tool_statue=True            
            
    if tool_statue:
        while not tool_data.empty():
            python:
                data=tool_data.get()
                root_logger.info(f"调用tool:{data}")
                tools_caller.caller(data)
        $ result_statue=True

    python:
        if result_statue:
            root_logger.info("获取tool结果")
            result_statue=False
            messages=[]
            while not renpy.store.tool_result.empty():
                payload = {
                    "role": "tool",
                    "content": str(renpy.store.tool_result.get()),
                    "tool_call_id": tool_id.get()
                }
                messages.append(payload)
                
            eid=eventloop.add_event(chat.send,messages)
            while eventloop.event_results[eid]["status"] == "pending":
                time.sleep(0.1)
            if eventloop.event_results[eid]["status"] == "completed":
                reply=eventloop.get_event_result(eid).get("result")
            else:
                error=eventloop.get_event_result(eid)
                raise error.get("result")

            renpy.store.reply_ready=True
            renpy.jump("main_loop")

    python:
        if reply.get("content"):
            if game_config.tts:
                # 翻译为日语
                eid=eventloop.add_event(translator.send,{"role":"user","content":reply.get("content")})
                renpy.notify("翻译中")
                while eventloop.event_results[eid]["status"] == "pending":
                    time.sleep(0.1)
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
                        time.sleep(0.1)
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
                        tts_ready=False
                        renpy.notify("合成语音失败")
                        root_logger.info(f"语音合成失败: {audio}")

                else:
                    renpy.notify("翻译格式转换失败")
                    root_logger.info(f"failed to load json: {ja_reply}")
                    tts_ready=False

            # 播放音频+显示消息
            if tts_ready:
                renpy.play(AudioData(renpy.store.tts_audio,"wav"))
                renpy.store.tts_filename=reply.get("content")[:10]
            renpy.say(noa,reply.get("content"))

    return

label main_loop:
    while True:
        python:
            if renpy.store.reply_ready:
                renpy.store.reply_ready=False
                renpy.call("message_processor",renpy.store.reply)
            message=renpy.input("sensei")

            if message:
                eid=eventloop.add_event(chat.send,{"role":"user","content":message})
                while eventloop.event_results[eid]["status"] == "pending":
                    time.sleep(0.1)
                if eventloop.event_results[eid]["status"] == "completed":
                    reply=eventloop.get_event_result(eid).get("result")
                else:
                    error=eventloop.get_event_result(eid)
                    raise error.get("result")

                renpy.call("message_processor",reply)
            else:
                renpy.say(noa,"输入不能为空，请重新输入。")
    return
