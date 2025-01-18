init -999 python:
    import logging

    class LogCaptureHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.logs = []

        def emit(self, record):
            if len(self.logs) > 1000:
                self.logs=self.logs[100:]
            self.logs.append(self.format(record))

    # 创建自定义处理器
    log_capture_handler = LogCaptureHandler()
    log_capture_handler.setLevel(logging.DEBUG)  # 设置捕获所有级别的日志
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_capture_handler.setFormatter(formatter)

    # 获取根日志记录器并添加处理器
    root_logger = logging.getLogger("root")
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(log_capture_handler)

    import os
    if not os.path.exists(os.path.join(renpy.config.gamedir, "history")):
        os.makedirs(history_dir)
    if not os.path.exists(os.path.join(renpy.config.gamedir, "config.json")):
        with open(os.path.join(renpy.config.gamedir,"config.json"), "w", encoding="utf-8") as file:
            data = {
                    "chatglm_api_key": "",
                    "deepseek_api_key": "",
                    "siliconflow_api_key":"",
                    "model": "glm-4-flash",
                    "tts": true,
                    "limit": "8k",
                    "proxy": {
                        "http": null,
                        "https": null
                    }
                }
            json.dump(data, file, indent=4, ensure_ascii=False)
            
init 2 python:
    import title_changer
    from deepseek import DeepSeek
    from api_ver import Base_llm
    import time
    import queue
    import audio_generator
    from io import BytesIO

init 3 python:
    dirs=tools_caller.get_dirs(os.path.join(renpy.config.gamedir, "images/background"))
    tools = [
        {
            "type": "function",
            "function": {
                "name": "control_character",
                "description": "control the character's position, emotion, emoji, action,effect,and scaleup",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "position": {
                            "type": "string",
                            "description": "position of the character, choose from the following:1~5"
                        },
                        "emotion": {
                            "type": "string",
                            "description": "character's emotion, choose from the following:joy,sadness,anger,surprise,fear,disgust,normal,embarrassed"
                        },
                        "emoji": {
                            "type": "string",
                            "description": "display an emoji above a character's head or in a chat bubble,choose from the following:angry,bulb,chat,dot,exclaim,heart,music,question,respond,sad,shy,sigh,steam,surprise,sweat,tear,think,twinkle,upset,zzz"
                        },
                        "action": {
                            "type": "string",
                            "description": "character's action, choose from the following:sightly_down,fall_left,fall_right,jump,jump_more"
                        },
                        "effect": {
                            "type": "string",
                            "description": "character's effect, choose from the following:hide(use hide to hide the character),holography(use when chat through phone)"
                        },
                        "scaleup":{
                            "type": "string",
                            "description": "scale up the character when approaching the speaker, choose from the following:scaleup"
                        }
                    },
                    "required": ["position", "emotion"]
                }
            }
        },
        {   
            "type": "function",
            "function": {
                "name": "dir_walker",
                "description": "get file names in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir": {
                            "type": "string",
                            "description": f"directory name, choose from the following:{dirs}",
                        }
                    },
                    "required": ["dir"],
                },
            }
        },
        {   
            "type": "function",
            "function": {
                "name": "bg_changer",
                "description": "chane the background image,use api 'dir_walker' to get the file names",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": f"directory/file,example:park/park.jpg",
                        }
                    },
                    "required": ["name"],
                },
            }
        }
    ]

    with open(os.path.join(renpy.config.gamedir,"config.json"), "r", encoding="utf-8") as file:
        game_config=json.load(file)

    storage_dir=os.path.join(renpy.config.gamedir, "history")
    with open(os.path.join(renpy.config.gamedir,"promot.txt"), "r", encoding="utf-8") as file:
        complex_prompt = file.read()
    llm = Base_llm( base_url="https://api.deepseek.com",
                    model="deepseek-chat", 
                    api_key=game_config.get("deepseek_api_key"), 
                    storage=storage_dir,
                    system_prompt=complex_prompt, 
                    tools=tools, 
                    limit=game_config.get("limit"),
                    proxy=game_config.get("proxy"))
    
    with open(os.path.join(renpy.config.gamedir,"translator.txt"), "r", encoding="utf-8") as file:
        translator_prompt = file.read()
    translator = Base_llm(api_key=game_config.get("chatglm_api_key"), 
                    storage="",
                    model="glm-4-flash", 
                    system_prompt=translator_prompt, 
                    limit=game_config.get("limit"),
                    proxy=game_config.get("proxy"))
    # translator = Base_llm(base_url="https://api.siliconflow.cn/v1", 
    #                     # model="Qwen/Qwen2.5-7B-Instruct",
    #                     model="THUDM/glm-4-9b-chat",
    #                     api_key=game_config.get("siliconflow_api_key"),
    #                     limit=game_config.get("limit"),
    #                     system_prompt=translator_prompt, 
    #                     storage="",
    #                     proxy=game_config.get("proxy"))  # type: ignore

    if game_config.get("tts"):
        import subprocess
        tts_terminal_output=[]
        def read_output(stream):
            global tts_terminal_output
            for line in stream:
                if len(tts_terminal_output)>1000:
                    tts_terminal_output=tts_terminal_output[-1000:]
                tts_terminal_output.append(line.decode("gbk").strip())
        
        # bat_file_path = os.path.join(renpy.config.gamedir,"GPT-SoVITS-v2-240821","GPT-SoVITS-v2-240821","api.bat")
        bat_file_path = r"D:\GPT-SoVITS-v2-240821\GPT-SoVITS-v2-240821\api.bat"

        process = subprocess.Popen(
            bat_file_path,
            # cwd=os.path.join(renpy.config.gamedir,"GPT-SoVITS-v2-240821","GPT-SoVITS-v2-240821"),
            cwd=r"D:\GPT-SoVITS-v2-240821\GPT-SoVITS-v2-240821",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        renpy.invoke_in_thread(read_output, process.stdout)
        renpy.invoke_in_thread(read_output, process.stderr)

        tts_refer=load_gsv_refer()
        tts=audio_generator.Audio_generator()
        renpy.invoke_in_thread(tts.run)

    else:
        tts_terminal_output=[]
init 4 python:
    renpy.invoke_in_thread(llm.run)
    renpy.invoke_in_thread(translator.run)

init 5 python:
    config.keymap['rollback'].remove('anyrepeat_K_PAGEUP')
    config.keymap['rollback'].remove('anyrepeat_KP_PAGEUP')
    config.keymap['rollback'].remove('K_AC_BACK')
    config.keymap['rollback'].remove('mousedown_4')

    if game_config.get("tts"):
        while  True:
            if "INFO:     Uvicorn running on http://127.0.0.1:9880 (Press CTRL+C to quit)" in tts_terminal_output:
                break
            time.sleep(0.1)
        def close_tts():
            tts.exit()
        config.quit_callbacks.append(close_tts)

screen entry():
    python:
        llm.event.put("get_conversations")
        while not llm.ready:
            time.sleep(0.1)
        llm.ready=False
        conversation_list=llm.result.get()
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
            action [Function(llm.clear_history),
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
    hide screen entry
    show loading
    python:
        if not new_conversation:
            latest_message=llm.get_latest_message(llm.chat_history)
            control_recall=llm.latest_tool_recall(llm.chat_history,"control_character")
            bg_recall=llm.latest_tool_recall(llm.chat_history,"bg_changer")

            recall_data=queue.Queue()
            if control_recall and not control_recall.empty():
                while not control_recall.empty():
                    recall_data.put(control_recall.get())
            if bg_recall and not bg_recall.empty():
                while not bg_recall.empty():
                    recall_data.put(bg_recall.get())

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
                    logging.info("recalling...")
                    data=recall_data.get()
                    if data.get("name") in tool_call_counts:
                        renpy.store.tool_call_counts[data.get("name")]+=1
                    tools_caller.caller(data)
                    
    python:
        if recall_statue:
            logging.info(renpy.store.tool_call_counts)
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
        logging.info(reply)
        tool_statue=False
        tool_data=queue.Queue()
        result_statue=False
        renpy.store.tool_result=queue.Queue()
        tool_id=queue.Queue()
        tts_ready=False
        logging.info("开始处理消息")

    python:
        if reply.get("tool_calls"):
            logging.info("获取tool参数")
            for tool in reply.get("tool_calls"):
                tool_id.put(tool.get("id"))
                function=tool.get("function")
                tool_data.put(function)
            tool_statue=True            
            
    if tool_statue:
        while not tool_data.empty():
            python:
                data=tool_data.get()
                logging.info(f"调用tool:{data}")
                tools_caller.caller(data)
        $ result_statue=True

    python:
        if result_statue:
            logging.info("获取tool结果")
            result_statue=False
            messages=[]
            while not renpy.store.tool_result.empty():
                payload = {
                    "role": "tool",
                    "content": str(renpy.store.tool_result.get()),
                    "tool_call_id": tool_id.get()
                }
                messages.append(payload)
                
            llm.event.put(("send",(messages,)))
            while not llm.ready:
                renpy.pause(0.1)
            llm.ready=False
            reply=llm.result.get()
            renpy.store.reply_ready=True
            renpy.jump("main_loop")

    python:
        if reply.get("content"):
            if game_config.get("tts"):
                translator.event.put(("send",({"role":"user","content":reply.get("content")},)))
                renpy.notify("翻译中")
                while not translator.ready:
                    renpy.pause(0.1)
                translator.ready=False
                ja_reply=translator.result.get()
                translator.clear_history()
                renpy.notify("翻译完成")
                try:
                    ja_reply=json.loads(ja_reply.get("content"))
                    ja_load=True
                except:
                    logging.info("failed to load json")
                    ja_load=False
                if ja_load:
                    ja=ja_reply.get("text")
                    emotion=ja_reply.get("emotion")
                    logging.info(f"ja:{ja}")
                    logging.info(f"emotion:{emotion}")

                    refer = tts_refer.get(emotion)
                    if not refer:
                        refer = tts_refer.get("normal")
                    refer_path=os.path.join(renpy.config.gamedir, "audio", "gsv",refer[0])
                    refer_text=refer[1]
                    refer_data={"refer_wav_path": refer_path, "prompt_text": refer_text, "prompt_language": "all_ja"}
                   
                    tts.event.put(
                        ("gen", {"text": ja, "language": "ja", "refer_data": refer_data}))
                    renpy.notify("合成语音中")
                    while not tts.ready:
                        renpy.pause(0.1)
                    tts.ready=False
                    audio=tts.result.get()
                    if isinstance(audio,BytesIO):
                        renpy.store.tts_audio=audio.getvalue()
                        tts_ready=True
                        renpy.notify("合成语音成功")
                    else:
                        tts_ready=False
                        logging.info(f"语音合成失败: {audio}")
                else:
                    renpy.notify("翻译格式转换失败")
                    logging.info(f"failed to load json: {ja_reply}")
                    tts_ready=False

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
                llm.event.put(("send",({"role":"user","content":message},)))
                while not llm.ready:
                    renpy.pause(0.1)
                llm.ready=False
                reply=llm.result.get()
                renpy.call("message_processor",reply)
            else:
                renpy.say(noa,"输入不能为空，请重新输入。")
    return
