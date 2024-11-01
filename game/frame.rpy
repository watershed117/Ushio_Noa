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

# screen emoji(position,emotion,emoji=None,emoji_atl=None,frame_atl=None):
#     tag emoji
#     frame at frame_atl:
#         xsize 754
#         ysize 1351
#         pos position_map[position]
#         background None
#         add "ushio_noa [emotion]"
#         if emoji:
#             add "emoji [emoji]" at emoji_atl

# label emoji(position,emotion,emoji=None,emoji_atl=None,frame_atl=None):
#     show screen emoji(position,emotion,emoji,emoji_atl,frame_atl)
#     play sound "audio/emotion/[emoji].wav"

screen angry(position,emotion,atl=None):
    tag emoji
    frame at atl:
        xsize 754
        ysize 1351
        pos position_map[position]
        background None
        add "ushio_noa [emotion]"
        add "emoji angry" at emoji_angry

label angry(position,emotion,atl=None):
    show screen angry(position,emotion,atl)
    play sound "audio/emotion/angry.wav"
    return

screen bulb(position,emotion,atl=None):
    tag emoji
    frame at atl:
        xsize 754
        ysize 1351
        pos position_map[position]
        background None
        add "ushio_noa [emotion]"
        add "emoji bulb" at emoji_bulb

label bulb(position,emotion,atl=None):
    show screen bulb(position,emotion,atl)
    play sound "audio/emotion/bulb.wav"
    return

screen chat(position,emotion,atl=None):
    tag emoji
    frame at atl:
        xsize 754
        ysize 1351
        pos position_map[position]
        background None
        add "ushio_noa [emotion]"
        add "emoji chat" at emoji_chat

label chat(position,emotion,atl=None):
    show screen chat(position,emotion,atl)
    play sound "audio/emotion/chat.wav"
    return 

screen dot(position,emotion,atl=None):
    tag emoji
    frame at atl:
        xsize 754
        ysize 1351
        pos position_map[position]
        background None
        add "ushio_noa [emotion]"
        add "emoji dot2" at emoji_bulb
        add "dot"


label dot(position,emotion,atl=None):
    show screen dot(position,emotion,atl)
    pause 0.5
    play sound "audio/emotion/dot.wav"
    return 

screen exclaim(position,emotion,atl=None):
    tag emoji
    frame at atl:
        xsize 754
        ysize 1351
        pos position_map[position]
        background None
        add "ushio_noa [emotion]"
        add "emoji exclaim" at emoji_exclaim

label exclaim(position,emotion,atl=None):
    show screen exclaim(position,emotion,atl)
    play sound "audio/emotion/exclaim.wav"
    return 

screen heart(position,emotion,atl=None):
    tag emoji
    frame at atl:
        xsize 754
        ysize 1351
        pos position_map[position]
        background None
        add "ushio_noa [emotion]"
        add "emoji dot2" at emoji_bulb 
        add "emoji heart" at emoji_heart

label heart(position,emotion,atl=None):
    show screen heart(position,emotion,atl)
    play sound "audio/emotion/heart.wav"
    return 

screen music(position,emotion,atl=None):
    tag emoji
    frame at atl:
        xsize 754
        ysize 1351
        pos position_map[position]
        background None
        add "ushio_noa [emotion]"
        add "emoji music" at emoji_music    

label music(position,emotion,atl=None): 
    show screen music(position,emotion,atl)
    play sound "audio/emotion/music.wav"
    return

