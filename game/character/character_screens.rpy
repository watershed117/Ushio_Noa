screen noa_blink(position):
    tag noa
    frame:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        add "noa_blink"

# screen noa_normal_close(position):
#     tag noa
#     frame:
#         xsize 754
#         ysize 1351
#         pos position_map[position]
#         background None
#         add "ushio_noa normal_close"

# screen noa_joy_close(position):
#     tag noa
#     frame:
#         xsize 754
#         ysize 1351
#         pos position_map[position]
#         background None
#         add "ushio_noa joy_close"

# screen emoji(position,emotion,emoji=None,emoji_action=None,frame_action=None):
#     tag emoji
#     frame at frame_action:
#         xsize 754
#         ysize 1351
#         pos position_map[position]
#         background None
#         add "ushio_noa [emotion]"
#         if emoji:
#             add "emoji [emoji]" at emoji_action

# label emoji(position,emotion,emoji=None,emoji_action=None,frame_action=None):
#     show screen emoji(position,emotion,emoji,emoji_action,frame_action)
#     play sound "audio/emotion/[emoji].wav"

screen angry(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji angry" at emoji_angry
        on "show" action Play("sound","audio/emotion/angry.wav")

screen bulb(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji bulb" at emoji_bulb
        on "show" action Play("sound","audio/emotion/bulb.wav")

screen chat(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji chat" at emoji_chat
        on "show" action Play("sound","audio/emotion/chat.wav")

screen dot(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji dot2" at emoji_bulb
        add "emoji dot"
        on "show" action Play("sound","audio/emotion/dot.wav")

screen exclaim(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji exclaim" at emoji_exclaim
        on "show" action Play("sound","audio/emotion/exclaim.wav")

screen heart(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji dot2" at emoji_bulb 
        add "emoji heart" at emoji_heart
        on "show" action Play("sound","audio/emotion/heart.wav")

screen music(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji music" at emoji_music
        on "show" action Play("sound","audio/emotion/music.wav")

screen question(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji question" at emoji_question
        on "show" action Play("sound","audio/emotion/question.wav")

screen respond(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji respond" at emoji_respond
        on "show" action Play("sound","audio/emotion/respond.wav")

screen sad(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji sad" at emoji_sad
        on "show" action Play("sound","audio/emotion/sad.wav")

screen shy(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 1351        
        pos position_map[position]
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji dot2" at shy_base
        add "emoji shy" at emoji_shy
        on "show" action Play("sound","audio/emotion/shy.wav")

screen sigh(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji sigh" at emoji_sigh
        on "show" action Play("sound","audio/emotion/sigh.wav")

screen steam(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji steam" at emoji_steam
        on "show" action Play("sound","audio/emotion/steam.wav")

screen surprise(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754        
        ysize 1351
        pos position_map[position]
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji surprise1" at emoji_surprise1
        add "emoji surprise2" at emoji_surprise2
        on "show" action Play("sound","audio/emotion/surprise.wav")

screen sweat(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji sweat" at emoji_sweat
        on "show" action Play("sound","audio/emotion/sweat.wav")

screen tear(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji tear"
        on "show" action Play("sound","audio/emotion/tear.wav")

# init python:
#     def randint(a, b):
#         renpy.random_num = renpy.random.randint(a, b)
# default random_num = 1

screen think(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji think0" at emoji_think
        # on "show" action Function(randint,1,3)
        $ random_num = renpy.random.randint(1, 3)
        if random_num == 1:
            add "emoji think1" at ice
        elif random_num == 2:
            add "emoji think2" at ice
        else:
            add "emoji think1" at ice
        on "show" action Play("sound","audio/emotion/think.wav")

screen twinkle(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji twinkle" at emoji_twinkle1
        add "emoji twinkle" at emoji_twinkle2
        add "emoji twinkle" at emoji_twinkle3
        on "show" action Play("sound","audio/emotion/twinkle.wav")

screen upset(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji dot2" at emoji_think
        add "emoji upset" at emoji_upset
        on "show" action Play("sound","audio/emotion/upset.wav")

screen zzz(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at scaleup,action:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji zzz"
    on "show" action Play("sound","audio/emotion/zzz.wav")

label zzz_(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen zzz(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/zzz.wav"
    return

screen noa_base(position,emotion,action=blank,scaleup=blank,transition=blank):
    tag emoji
    frame at action,scaleup:
        xsize 754
        ysize 880
        pos position_map[position]
        if scaleup==blank:
            pass
        else:
            if action==down:
                xoffset -125
            elif action==left_down:
                xoffset -225
                yoffset -70
            elif action==right_down:
                xoffset -225
                yoffset -70
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
