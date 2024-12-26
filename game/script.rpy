init 1 python:
    import title_changer
    import api_ver
    import os
    import game_config
    import time
    import queue
    import json
    import audio_generator
    from io import BytesIO

init 2 python:
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
                "description": "chane the background image,use dir_walker to get the file names",
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
    storage_dir=os.path.join(renpy.config.gamedir, "history")
    with open(os.path.join(renpy.config.gamedir,"test.txt"), "r", encoding="utf-8") as file:
        complex_prompt = file.read()
    chatglm = api_ver.ChatGLM(api_key=game_config.api_key, 
                    storage=storage_dir,
                    model=game_config.model, 
                    system_prompt=complex_prompt, 
                    tools=tools, 
                    limit=game_config.limit,
                    proxy=game_config.proxy)
    
    with open(os.path.join(renpy.config.gamedir,"translator.txt"), "r", encoding="utf-8") as file:
        translator_prompt = file.read()
    translator = api_ver.ChatGLM(api_key=game_config.api_key, 
                    storage="",
                    model="glm-4-flash", 
                    system_prompt=translator_prompt, 
                    limit=game_config.limit,
                    proxy=game_config.proxy)

    if game_config.tts:
        tts=audio_generator.Audio_generator()
        renpy.invoke_in_thread(tts.run)

init 3 python:
    info_path=os.path.join(renpy.config.gamedir, "info.json")
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

init 4 python:
    renpy.invoke_in_thread(chatglm.run)
    renpy.invoke_in_thread(translator.run)

init 5 python:
    config.keymap['rollback'].remove('anyrepeat_K_PAGEUP')
    config.keymap['rollback'].remove('anyrepeat_KP_PAGEUP')
    config.keymap['rollback'].remove('K_AC_BACK')
    config.keymap['rollback'].remove('mousedown_4')

screen entry():
    python:
        chatglm.event.put("get_conversations")
        while not chatglm.ready:
            time.sleep(0.1)
        chatglm.ready=False
        conversation_list=chatglm.result.get()
    add "images/ui/ui.png"
    default conversation_number=len(conversation_list)
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
            # action Function(print, "新建会话")
            action [Function(chatglm.clear_history),
                    SetVariable("new_conversation",True),
                    Jump("main")]
        if conversation_number:
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
                        action [Function(chatglm.event.put, 
                                        ("load",
                                        (conversation_list[n].get("id"),))),
                                Function(change_title,conversation_list[n].get("id")),
                                Jump("main")]
                        

default position_map={
    "1": (0, 200),
    "2": (300, 200),
    "3": (600, 200),
    "4": (900, 200),
    "5": (1200, 200)
}


# define noa = Character(name="{font=MPLUS1p-Bold.ttf}{color=#ffffff}{size=64}乃愛{/size}{/color}{/font}{font=MPLUS1p-Bold.ttf}{color=#7cd0ff}{size=32}研討會{/size}{/color}{/font}") 
define noa = Character(name="乃愛 研討會",
                        # who_size=40,
                        # who_outlines=[ (1, "#284058", 0, 0 ) ],
                        # who_color="#ffffff",
                        # who_font="fonts/MPLUS1p-Bold.ttf",
                        what_size=32,
                        what_color="#ffffff",
                        what_outlines=[ (2, "#284058", 0, 0 ) ],
                        what_font="fonts/SourceHanSansCN-Bold.otf",
                        what_yoffset=65,
                        what_xoffset=-37,
                        window_background="images/ui/say.png",
                        window_yoffset=-100) 

# label start:
#     $ result=tools_caller.control_character("3","joy",action=jump)
#     noa "[result]"
#     pause

label start:
    stop music fadeout 1.0
    call screen entry()

label ready:
    show ready with CropMove(1.0, "wipedown")
    hide loading
    return

default new_conversation=False
label main:
    hide screen entry
    show loading
    python:
        if not new_conversation:
            while not chatglm.ready:
                renpy.pause(0.1)
            chatglm.ready=False
            chatglm.result.get()
            latset_tools_data=chatglm.latest_tool_recall(chatglm.history)
            latest_message=chatglm.get_latest_message(chatglm.history)
            # print(latset_tools_data)
            # print(latest_message)
            renpy.call("ready")

    if not new_conversation:
        if latset_tools_data:
            while not latset_tools_data.empty():
                $ tools_caller.caller(latset_tools_data.get())
                    
    python:
        if not new_conversation:
            if not latset_tools_data:
                renpy.show_screen("noa_base","3","joy")
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

default tool_statue=False
default tool_data=queue.Queue()
default result_statue=False
default tool_result=queue.Queue()
default reply=""
default reply_ready=False
default tts_audio=None
default tts_ready=False
default tts_filename=""
label message_processor(reply):
    $ print(reply)
    python:
        while not renpy.store.tool_data.empty():
            renpy.store.tool_data.get()
        while not renpy.store.tool_result.empty():
            renpy.store.tool_result.get()
        print("清空tool数据")

    python:
        if reply.get("tool_calls"):
            print("获取tool参数")
            renpy.store.tool_data=queue.Queue()
            for tool in reply.get("tool_calls"):
                function=tool.get("function")
                renpy.store.tool_data.put(function)
            renpy.store.tool_statue=True

    python:
        if renpy.store.tool_statue:
            print("调用tool")
            renpy.store.tool_statue=False
            renpy.store.result_statue=True
            while not renpy.store.tool_data.empty():
                tools_caller.caller(renpy.store.tool_data.get())

    python:
        if renpy.store.result_statue:
            print("获取tool结果")
            renpy.store.result_statue=False
            result=[]
            while not renpy.store.tool_result.empty():
                result.append(renpy.store.tool_result.get())
            chatglm.event.put(("send",({"role":"tool","content":str(result)},)))
            while not chatglm.ready:
                renpy.pause(0.1)
            chatglm.ready=False
            renpy.store.reply=chatglm.result.get()
            renpy.store.reply_ready=True
            renpy.jump("main_loop")
    python:
        if reply.get("content"):
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
                print("failed to load json")
                ja_load=False
            if ja_load:
                ja=ja_reply.get("text")
                emotion=ja_reply.get("emotion")
                print(f"ja:{ja}")
                print(f"emotion:{emotion}")


                refer_data = {"refer_wav_path": r"D:\GPT-SoVITS-v2-240821\GPT-SoVITS-v2-240821\output\noa\noa_153.wav",
                            "prompt_text": "それならゆうかちゃんの声が流れる目覚まし時計とかいいかもしれませんね",
                            "prompt_language": "ja"}


                renpy.notify("合成语音中")
                tts.event.put(
                    ("gen", {"text": ja, "language": "ja", "refer_data": refer_data}))
                while not tts.ready:
                    renpy.pause(0.1)
                tts.ready=False
                audio=tts.result.get()
                if isinstance(audio,BytesIO):
                    renpy.store.tts_audio=audio.getvalue()
                    renpy.store.tts_ready=True
                    renpy.notify("合成语音成功")
                else:
                    renpy.store.tts_ready=False
                    print(f"语音合成失败: {audio}")
            else:
                renpy.notify("翻译格式转换失败")
                print(f"failed to load json: {ja_reply}")
                renpy.store.tts_ready=False
            if renpy.store.tts_ready:
                renpy.play(AudioData(renpy.store.tts_audio,"wav"))
                renpy.store.tts_filename=reply.get("content")[:10]
            renpy.say(noa,reply.get("content"))

        renpy.jump("main_loop")

    return

label main_loop:
    while True:
        python:
            if renpy.store.reply_ready:
                renpy.store.reply_ready=False
                renpy.call("message_processor",renpy.store.reply)
            message=renpy.input("sensei")
            if message:
                chatglm.event.put(("send",({"role":"user","content":message},)))
                while not chatglm.ready:
                    renpy.pause(0.1)
                chatglm.ready=False
                reply=chatglm.result.get()
                renpy.call("message_processor",reply)
            else:
                renpy.say(noa,"输入不能为空，请重新输入。")
    return
