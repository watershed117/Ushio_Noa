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

label ready:
    show ready with CropMove(1.0, "wipedown")
    hide loading
    return

label main:
    python:
        renpy.hide_screen("entry")
        renpy.show("loading")
        if not renpy.store.new_conversation:
            latest_message=chat.get_latest_message(chat.store_history)
            control_recall=chat.latest_tool_recall(agent.store_history,"control_character")
            bg_recall=chat.latest_tool_recall(agent.store_history,"bg_changer")
            if control_recall:
                renpy.store.tool_call_counts["control_character"]+=1
            if bg_recall:
                renpy.store.tool_call_counts["bg_changer"]+=1
            result = chat_tool_collection.tool_calls_handler(control_recall+bg_recall)
            
            root_logger.info(renpy.store.tool_call_counts)
            if renpy.store.tool_call_counts.get("control_character")==0:
                renpy.show_screen("noa_base","3","joy")
            if renpy.store.tool_call_counts.get("bg_changer")==0:
                renpy.with_statement(None)
                renpy.scene()
                renpy.show("mainoffice")
                renpy.with_statement(dissolve)
            if latest_message:
                renpy.say(noa,latest_message)

        else:
            renpy.store.new_conversation=False
            renpy.show_screen("noa_base","3","normal")
            renpy.with_statement(None)
            renpy.scene()
            renpy.show("mainoffice")
            renpy.with_statement(dissolve)

        renpy.hide("ready")
        renpy.show_screen("main_ui")
        renpy.jump("main_loop")

label main_loop:
    python:
        while True:
            uploader.files=[]
            message = renpy.input("sensei")
            renpy.store.raw_message = message
            if not message:
                renpy.say(noa, "输入不能为空，请重新输入。")
                continue
            sys_messages = []
            if uploader.files:
                sys_messages.append(f"用户上传了文件，路径为{uploader.files}")
            
            sys_message="\n<sys>"+"\n".join(sys_messages)"</sys>\n"

            retrieval_message=

            reply = run_in_eventloop(
                                    chat.send,
                                    {"role": "user", "content": message+sys_message},
                                    raise_or_not=True
                                )
            handler(reply)
    return
