init -999 python:
    import json
    import os
    import time
    from chatglm_for_renpy import Chatglm
    from audio_generator import Auduio_generator
    from bs4 import BeautifulSoup
    import re
    # audio_byte=None
    face={"惊讶":"1.png","闭眼微笑":"2.png","微笑":"3.png","闭眼":"4.png","伤心":"5.png","尴尬":"6.png","严肃":"7.png","生气":"8.png","正常":"3.png","认真":"7.png","惊喜":"2.png"}
    # with open("./game/config.json","r") as file:
    with open(os.path.join(config.gamedir,"config.json"),"r") as file:
        data=json.loads(file.read())
        token=data.get("token")
        refresh_token=data.get("refresh_token")
        acw_tc=data.get("acw_tc")
        assistant_id=data.get("assistant_id")
        audio_generator_port=data.get("audio_generator_port")
define noa =Character("诺亚",image="noa_image")
default reply_list=["推荐回复"]
default face_list=["微笑"]
default audio_text=[""]
default message=""

image side noa_image joy="images/face/2.png"
image side noa_image sadness="images/face/5.png"
image side noa_image anger="images/face/8.png"
image side noa_image surprise="images/face/1.png"
image side noa_image fear="images/face/5.png"
image side noa_image disgust="images/face/7.png"
image side noa_image normal="images/face/3.png"
image side noa_image close="images/face/4.png"
image side noa_image embarrassed="images/face/6.png"


init -997 python:
    glm=Chatglm(token=token,
                refresh_token=refresh_token,
                acw_tc=acw_tc,
                assistant_id=assistant_id,
                conversation_id=""
                )
    gen = Auduio_generator(port=audio_generator_port)

init -996 python:
    def remove(text):
        pattern = r'\([^)]*\)|（[^）]*）'
        cleaned_text = re.sub(pattern, '', text,)
        return cleaned_text
    def chinese_decoder(soup:BeautifulSoup):
        chinese=soup.find("chinese")
        chinese_text=chinese.find_all("text")
        face=chinese.find_all("face")
        return chinese_text,face
        # if len(chinese_text) == len(face):
        #     return chinese_text,face
        # else:
        #     raise Exception("!=")
    def japanese_decoder(soup:BeautifulSoup):
        japanese=soup.find("japanese")
        japanese_text=japanese.find_all("text")
        emotion=japanese.find_all("emotion")
        return japanese_text,emotion
        # if len(japanese_text)==len(emotion):
        #     return japanese_text,emotion
        # else:
        #     raise Exception("!=")
    def get_conversations(data: tuple):
        global conversation_list,has_more
        if data[1]:
            conversation_list += data[0]
            glm.event_queue.put({"get_conversations": (data[2] + 1,)})
            while True:
                if glm.get_conversations_ready:
                    glm.get_conversations_ready=False
                    get_conversations(glm.get_conversations_output)
                else:
                    time.sleep(0.1)
        else:
            conversation_list += data[0]
            has_more=False
    def change(uuid:str):
        glm.conversation_id=uuid
        renpy.notify(uuid)
        renpy.jump("main")
    def msg_handle():
        while True:
            if glm.send_ready:
                glm.send_ready=False
                text=glm.send_output.get("text")
                soup = BeautifulSoup(text,features="html.parser")
                chinese,face=chinese_decoder(soup)
                japanese,emotion=japanese_decoder(soup)
                tmp=[]
                for item in chinese:
                    tmp.append(item.get_text())
                store.reply_list=tmp
                tmp=[]
                for item in face:
                    tmp.append(item.get_text())       
                store.face_list=tmp
                tmp=[]
                for item in japanese:
                    tmp.append(remove(item.get_text()))
                store.audio_text=tmp
                break
            else:
                renpy.pause(0)
    def new_conversation():
        with open(os.path.join(config.gamedir,"promot.txt"),"r") as file:
            prompt=file.read()
        glm.event_queue.put({"send":(prompt,"")})
        while True:
            if glm.send_ready:
                glm.send_ready=False
                text=glm.send_output.get("text")
                soup = BeautifulSoup(text,features="html.parser")
                chinese,face=chinese_decoder(soup)
                japanese,emotion=japanese_decoder(soup)
                tmp=[]
                for item in chinese:
                    tmp.append(item.get_text())
                store.reply_list=tmp
                tmp=[]
                for item in face:
                    tmp.append(item.get_text())       
                store.face_list=tmp
                tmp=[]
                for item in japanese:
                    tmp.append(remove(item.get_text()))
                store.audio_text=tmp
                break
            else:
                time.sleep(0.1)
        renpy.jump("tmp")
    # renpy.invoke_in_thread(glm.run)
    # glm.event_queue.put({"refresh":(glm.refresh_token,)})
    # while True:
    #     if glm.refresh_ready:
    #         break
    #     else:
    #         time.sleep(0.1)
    # renpy.invoke_in_thread(gen.run)

label tmp:
    hide screen entry
    scene bg
    show screen default_pic
    python:
        renpy.notify("新建会话成功")
        n=0
        for text in store.reply_list:
            gen.event_queue.put({"gen":(store.audio_text[n].strip(),"ja")})
            while True:
                if gen.gen_ready:
                    gen.gen_ready=False
                    renpy.hide_screen("default_pic")
                    renpy.hide_screen("full")
                    renpy.show_screen("full",store.face_list[n])
                    audio_byte=AudioData(gen.gen_output,"wav")
                    renpy.sound.play(audio_byte)
                    renpy.say("诺亚",text)
                    break
                else:
                    renpy.pause(0.1)
            n+=1
        renpy.jump("main")

screen page(conversation_number,conversation_list):
    viewport:
        #frame
        vbox:
            pos(1101,162)
            spacing 51
            for n in range(0,conversation_number):
                add "images/ui/frame.png"
        #text
        vbox:
            pos(1125, 185)
            spacing 105
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
            pos(1683, 170)
            spacing 63
            for n in range(0,conversation_number):
                button:
                    add "images/ui/button.png"
                    action Function(change,conversation_list[n].get("conversation_id"))
screen entry():
    default conversation_number=len(conversation_list)
    if conversation_number:
        viewport:
            pos(1101,162)
            xsize 800
            ysize 854
            mousewheel True
            scrollbars("vertical")
            #frame
            vbox:
                pos(0,0)
                spacing 51
                for n in range(0,conversation_number):
                    add "images/ui/frame.png"
            #text
            vbox:
                pos(30, 25)
                spacing 103
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
                pos(582,13)
                spacing 63
                for n in range(0,conversation_number):
                    button:
                        add "images/ui/button.png"
                        action Function(change,conversation_list[n].get("conversation_id"))
screen show_face(name):
    add "images/face/[face.get(name)]" pos (0, 766)
screen full(name):
    add "images/full/[face.get(name)]" pos(610,300)
screen default_pic:
    add "images/noa_default.png" pos(610,300)
label say_with_face(emo,text):
    # play sound audio_byte
    if emo=="惊讶":
        noa surprise "{cps=20}[text]{/cps}"
        return
    elif emo=="闭眼微笑":
        noa joy "{cps=20}[text]{/cps}"
        return
    elif emo=="微笑":
        noa normal "{cps=20}[text]{/cps}"
        return
    elif emo=="闭眼":
        noa close "{cps=20}[text]{/cps}"
        return
    elif emo=="伤心":
        noa sadness "{cps=20}[text]{/cps}"
        return
    elif emo=="尴尬":
        noa embarrassed "{cps=20}[text]{/cps}"
        return
    elif emo=="严肃":
        noa disgust "{cps=20}[text]{/cps}"
        return
    elif emo=="生气":
        noa anger "{cps=20}[text]{/cps}"
        return

label start:
    stop music fadeout 1.0
    call noa_blink
    pause
    # hide emoji
    call emoji_angry
    pause
    # hide emoji
    call emoji_bulb
    pause
    # hide emoji
    call emoji_chat
    pause
    # hide emoji
    call emoji_dot
    pause
    hide dot1
    hide dot2
    hide dot3
    # hide emoji
    call emoji_exclaim
    pause
    call emoji_heart 
    pause
    hide emoji
    hide basebulb
    call emoji_music
    pause
    noa ""
    return
    scene ui
    python:
        conversation_list=[]
        has_more=True
        glm.event_queue.put({"get_conversations":(1,)})
        while True:
            if glm.get_conversations_ready:
                glm.get_conversations_ready=False
                get_conversations(glm.get_conversations_output)
                break
            else:
                renpy.pause(0.1)
    call screen entry            
label main:
    hide ui
    hide screen entry
    scene bg
    show screen default_pic
    while True:
        $ glm.event_queue.put({"recommand":(glm.conversation_id,)})
        if glm.recommand_ready:
            $ glm.recommand_ready=False
            if glm.recommand_output:
                menu recommand:
                    noa normal "[reply_list[-1]]"
                    "[glm.recommand_output[0]]":
                        $ store.message=glm.recommand_output[0]
                    "[glm.recommand_output[1]]":
                        $ store.message=glm.recommand_output[1]
                    "[glm.recommand_output[2]]":
                        $ store.message=glm.recommand_output[2]
                    "手动输入":
                        $ store.message=renpy.input("我：")
                python:
                    glm.event_queue.put({"send":(store.message,glm.conversation_id,)})
                    msg_handle()
                    n=0
                    for text in store.reply_list:
                        gen.event_queue.put({"gen":(store.audio_text[n].strip(),"ja")})
                        while True:
                            if gen.gen_ready:
                                gen.gen_ready=False
                                renpy.hide_screen("default_pic")
                                renpy.hide_screen("full")
                                renpy.show_screen("full",store.face_list[n])
                                audio_byte=AudioData(gen.gen_output,"wav")
                                renpy.sound.play(audio_byte)
                                renpy.call("say_with_face",store.face_list[n],text)
                                break
                            else:
                                renpy.pause(0.1)
                        n+=1
            else:
                python:
                    store.message=renpy.input("我：")
                    glm.event_queue.put({"send":(store.message,glm.conversation_id,)})
                    msg_handle()
                    n=0
                    for text in store.reply_list:
                        gen.event_queue.put({"gen":(store.audio_text[n].strip(),"ja")})
                        while True:
                            if gen.gen_ready:
                                gen.gen_ready=False
                                renpy.hide_screen("default_pic")
                                renpy.hide_screen("full")
                                renpy.show_screen("full",store.face_list[n])
                                audio_byte=AudioData(gen.gen_output,"wav")
                                renpy.sound.play(audio_byte)
                                renpy.call("say_with_face",store.face_list[n],text)
                                break
                            else:
                                renpy.pause(0.1)
                        n+=1
        else:
            pause 0.1