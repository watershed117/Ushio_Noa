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

default position_map={
    "1": (0, 200),
    "2": (300, 200),
    "3": (600, 200),
    "4": (900, 200),
    "5": (1200, 200)
}

label start:
    image default_background="images/background/office/mainoffice.jpg"
    scene default_background
    stop music fadeout 1.0
    $ tools.control_character("3","joy","zzz",effect="holography")
    pause
    return
    # scene ui
    # python:
    #     conversation_list=[]
    #     has_more=True
    #     glm.event_queue.put({"get_conversations":(1,)})
    #     while True:
    #         if glm.get_conversations_ready:
    #             glm.get_conversations_ready=False
    #             get_conversations(glm.get_conversations_output)
    #             break
    #         else:
    #             renpy.pause(0.1)
    # call screen entry            