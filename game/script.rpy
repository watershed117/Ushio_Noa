init 1 python:
    import title_changer
    import api_ver
    import os
    import game_config
    import time

init 2 python:
    dirs=tools_caller.get_dirs(os.path.join(renpy.config.gamedir, "images/background"))
    tools = [
        {
            "type": "function",
            "function": {
                "name": "control_character",
                "description": "控制角色的立绘，表情，动作，特效，在人物情绪变化时调用",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "position": {
                            "type": "string",
                            "description": "显示立绘的位置，将屏幕水平分为五等份，从左向右位置分别命名为'1'~'5'"
                        },
                        "emotion": {
                            "type": "string",
                            "description": "要显示的立绘的表情，可选'joy','sadness','anger','surprise','fear','disgust','normal','embarrassed'"
                        },
                        "emoji": {
                            "type": "string",
                            "description": "要显示的表情符号动画，可选'angry','bulb','chat','dot','exclaim','heart','music','question','respond','sad','shy','sigh','steam','surprise','sweat','tear','think','twinkle','upset','zzz'"
                        },
                        "action": {
                            "type": "string",
                            "description": "要播放的动作，可选'sightly_down','fall_left','fall_right','jump','jump_more'"
                        },
                        "effect": {
                            "type": "string",
                            "description": "要附加在立绘上的特效，可选'scaleup','hide','holography'"
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
                "description": "获取目录下的所有文件名",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir": {
                            "type": "string",
                            "description": f"文件夹名，可选{dirs}",
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
                "description": "背景图片切换，在调用前应当通过dir_walker获取文件名",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": f"格式要求：文件夹名/文件名,例如park/park.jpg",
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
                    limit=game_config.limit)

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
default new_conversation=False
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

label start:
    stop music fadeout 1.0
    call screen entry()

label ready:
    show ready with CropMove(1.0, "wipedown")
    hide loading
    return

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
    python:
        if not new_conversation:
            if latset_tools_data:
                tools_caller.caller(latset_tools_data)
            else:
                tools_caller.control_character("3","joy")
                renpy.call("bg_changer", "office/mainoffice.jpg")
    python:
        if not new_conversation:
            if latest_message:
                renpy.say(noa,latest_message)
    python:
        if new_conversation:
            new_conversation=False
            tools_caller.control_character("3","joy")
            renpy.call("bg_changer", "office/mainoffice.jpg")
            
    jump main_loop
    return

label main_loop:
    python:
        renpy.hide("ready")
        while True:
            message=renpy.input("sensei")
            if message:
                chatglm.event.put(("send",({"role":"user","content":message},)))
                while not chatglm.ready:
                    renpy.pause(0.1)
                chatglm.ready=False
                reply=chatglm.result.get()
                print(reply)
                while True:
                    if reply:
                        if reply.get("content"):
                            renpy.say(noa,reply.get("content"))
                            break
                        if reply.get("tool_callas"):
                            result=tools_caller.caller(reply.get("tool_callas"))
                            chatglm.event.put(("send",({"role":"tool","content":result},)))
                            while not chatglm.ready:
                                renpy.pause(0.1)
                            chatglm.ready=False
                            reply=chatglm.result.get()
                    else:
                        raise Exception("No reply")
    return
