screen noa_blink(position):
    tag noa
    frame:
        xsize 754
        ysize 1351
        pos position_map[position]
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
        ysize 1351
        pos position_map[position]
        background None
        if transition=="hide":
            add "ushio_noa black"
        elif transition=="holo":
            add holo(f"ushio_noa {emotion}")
        else:
            add "ushio_noa [emotion]"
        add "emoji angry" at emoji_angry

label angry(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen angry(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/angry.wav"
    return

screen bulb(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji bulb" at emoji_bulb

label bulb(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen bulb(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/bulb.wav"
    return

screen chat(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji chat" at emoji_chat

label chat(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen chat(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/chat.wav"
    return 

screen dot(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji dot2" at emoji_bulb
        add "emoji dot"


label dot(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen dot(position,emotion,action,scaleup,transition)
    pause 0.5
    play sound "audio/emotion/dot.wav"
    return 

screen exclaim(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji exclaim" at emoji_exclaim

label exclaim(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen exclaim(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/exclaim.wav"
    return 

screen heart(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji dot2" at emoji_bulb 
        add "emoji heart" at emoji_heart

label heart(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen heart(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/heart.wav"
    return 

screen music(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji music" at emoji_music    

label music(position,emotion,action=blank,scaleup=blank,transition=blank): 
    show screen music(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/music.wav"
    return

screen question(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji question" at emoji_question

label question(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen question(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/question.wav"
    return 

screen respond(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji respond" at emoji_respond

label respond(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen respond(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/respond.wav"
    return 

screen sad(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji sad" at emoji_sad

label sad(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen sad(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/sad.wav"
    return

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

label shy(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen shy(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/shy.wav"
    return

screen sigh(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji sigh" at emoji_sigh

label sigh(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen sigh(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/sigh.wav"
    return

screen steam(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji steam" at emoji_steam

label steam(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen steam(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/steam.wav"
    return 

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

label surprise(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen surprise(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/surprise.wav"
    return

screen sweat(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji sweat" at emoji_sweat

label sweat(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen sweat(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/sweat.wav"
    return 

screen tear(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji tear"

label tear(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen tear(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/tear.wav"
    return

# init python:
#     def randint(a, b):
#         renpy.random_num = renpy.random.randint(a, b)
# default random_num = 1

screen think(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji think0" at emoji_think
        # on "show" action Function(randint,1,3)
        $ random_num = renpy.random.randint(1, 3)
        if random_num == 1:
            add "emoji think1" at ice
        elif random_num == 2:
            add "emoji think2" at ice
        else:
            add "emoji think1" at ice

label think(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen think(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/think.wav"
    return

screen twinkle(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji twinkle" at emoji_twinkle1
        add "emoji twinkle" at emoji_twinkle2
        add "emoji twinkle" at emoji_twinkle3

label twinkle(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen twinkle(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/twinkle.wav"
    return

screen upset(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji dot2" at emoji_think
        add "emoji upset" at emoji_upset
        
label upset(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen upset(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/upset.wav"
    return 

screen zzz(position,emotion,action=blank,scaleup=blank,transition=blank):
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
        add "emoji zzz"

label zzz(position,emotion,action=blank,scaleup=blank,transition=blank):
    show screen zzz(position,emotion,action,scaleup,transition)
    play sound "audio/emotion/zzz.wav"
    return

screen noa_base(position,emotion,action=blank,scaleup=blank,transition=blank):
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
