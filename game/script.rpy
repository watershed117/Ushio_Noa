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
    python:
        renpy.hide_screen("entry")
        renpy.show("loading")
        if not renpy.store.new_conversation:
            latest_message=chat.get_latest_message(chat.chat_history)
            control_recall=chat.latest_tool_recall(chat.chat_history,"control_character")
            bg_recall=chat.latest_tool_recall(chat.chat_history,"bg_changer")

            recall_data=queue.Queue()
            if control_recall:
                renpy.store.recall_data.put(control_recall[0])
            if bg_recall:
                renpy.store.recall_data.put(bg_recall[0])

            renpy.with_statement(None)
            renpy.show("ready")
            renpy.with_statement(CropMove(1.0, "wipedown"))

            while not recall_data.empty():
                root_logger.info("recalling...")
                data=recall_data.get()
                if data.get("name") in tool_call_counts:
                    renpy.store.tool_call_counts[data.get("name")]+=1
                tools_caller.caller(data)
            
            root_logger.info(renpy.store.tool_call_counts)
            if renpy.store.tool_call_counts.get("control_character")==0:
                renpy.show_screen("noa_base","3","joy")
            if renpy.store.tool_call_counts.get("bg_changer")==0:
                renpy.call("bg_changer", "office/mainoffice.jpg")

            if latest_message:
                renpy.say(noa,latest_message)

        else:
            renpy.store.new_conversation=False
            renpy.show_screen("noa_base","3","joy")
            renpy.with_statement(None)
            renpy.scene()
            renpy.show("mainoffice")
            renpy.with_statement(dissolve)

        renpy.hide("ready")
        renpy.show_screen("main_ui")
        renpy.jump("main_loop")

label message_processor(reply):
    python:
        root_logger.info(reply)
        tool_ids=[]
        tool_result=[]
        result_statue=False
        tts_ready=False

        if reply.get("tool_calls"):
            root_logger.info("获取tool参数")
            for tool in reply.get("tool_calls"):
                tool_ids.append(tool.get("id"))
                function=tool.get("function")
                root_logger.info(f"调用tool:{function}")
                renpy.invoke_in_thread(tools_caller.caller,function)

            messages=[]
            for tool_id in tool_ids:
                while True:
                    if tools_caller.tool_result.empty():
                        renpy.pause(0.1)
                    else:
                        payload = {
                            "role": "tool",
                            "content": str(tools_caller.tool_result.get()),
                            "tool_call_id": tool_id
                        }
                        messages.append(payload)
                        break

            root_logger.info(f"send tool result:{messages}")   
            eid=eventloop.add_event(chat.send,messages)
            while eventloop.event_results[eid]["status"] == "pending":
                renpy.pause(0.1)
            if eventloop.event_results[eid]["status"] == "completed":
                renpy.store.reply=eventloop.get_event_result(eid).get("result")
            else:
                error=eventloop.get_event_result(eid)
                raise error.get("result")

            renpy.store.reply_ready=True

        if reply.get("content"):
            if game_config.tts:
                # 翻译为日语
                eid=eventloop.add_event(translator.send,{"role":"user","content":reply.get("content")})
                renpy.notify("翻译中")
                while eventloop.event_results[eid]["status"] == "pending":
                    renpy.pause(0.1)
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
            # renpy.invoke_in_main_thread(renpy.say,"noa",reply.get("content"))
            renpy.say(noa,reply.get("content"))

    jump main_loop
    return

# label main_loop:
#     while True:
#         python:
#             if renpy.store.reply_ready:
#                 renpy.store.reply_ready=False
#                 renpy.call("message_processor",renpy.store.reply)
#             uploader.files=[]
#             message=renpy.input("sensei")

#             if message:
#                 if uploader.files:
#                     message=f"<sys>用户上传了文件，路径为{uploader.files}</sys>"+message
#                 eid=eventloop.add_event(chat.send,{"role":"user","content":message})
#                 while eventloop.event_results[eid]["status"] == "pending":
#                     renpy.pause(0.1)
#                 if eventloop.event_results[eid]["status"] == "completed":
#                     reply=eventloop.get_event_result(eid).get("result")
#                 else:
#                     error=eventloop.get_event_result(eid)
#                     raise error.get("result")

#                 renpy.call("message_processor",reply)
#             else:
#                 renpy.say(noa,"输入不能为空，请重新输入。")
#     return

# label main_loop:
#     python: 
#         while True:
#             uploader.files=[]
#             message=renpy.input("sensei")
#             if message:
#                 if uploader.files:
#                     message=f"<sys>用户上传了文件，路径为{uploader.files}</sys>"+message
#                 eid=eventloop.add_event(chat.send,{"role":"user","content":message})
#                 while eventloop.event_results[eid]["status"] == "pending":
#                     renpy.pause(0.1)
#                 if eventloop.event_results[eid]["status"] == "completed":
#                     reply=eventloop.get_event_result(eid).get("result")
#                 else:
#                     error=eventloop.get_event_result(eid)
#                     raise error.get("result")
#             else:
#                 renpy.say(noa,"输入不能为空，请重新输入。")

#             # handle_reply(reply)
#             renpy.invoke_in_thread(handle_reply,reply)
#             while True:
#                 if not renpy.store.reply_handle_status:
#                     renpy.pause(0.1)
#                 else:
#                     renpy.store.reply_handle_status=False
#                     break
#     return

label main_loop:
    python:
        while True:
            uploader.files=[]
            # 1. 获取用户输入 (在循环开始时)
            message = renpy.input("sensei")

            # 2. 输入为空的处理
            if not message:
                renpy.say(noa, "输入不能为空，请重新输入。")
                continue  # 跳过本次循环，重新获取输入

            # 3. 处理文件上传 (如果存在)
            if uploader.files:
                message = f"<sys>用户上传了文件，路径为{uploader.files}</sys>"+message

            # 4. 发送消息并等待结果
            eid = eventloop.add_event(chat.send, {"role": "user", "content": message})
            while eventloop.event_results[eid]["status"] == "pending":
                renpy.pause(0.1)

            # 5. 处理结果 (成功或失败)
            if eventloop.event_results[eid]["status"] == "completed":
                reply = eventloop.get_event_result(eid).get("result")
            else:
                error = eventloop.get_event_result(eid)
                raise error.get("result")

            handle_reply(reply)

    return
