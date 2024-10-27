layeredimage ushio_noa:
    always:
        "layers/base.png"
    group face:
        attribute joy:
            "layers/2.png"
        attribute sadness:
            "layers/4.png"
        attribute anger:
            "layers/6.png"
        attribute surprise:
            "layers/5.png"
        attribute fear:
            "layers/4.png"
        attribute disgust:
            "layers/7.png"
        attribute normal default:
            "layers/2.png"
        attribute embarrassed:
            "layers/5.png"
        attribute normal_close:
            "layers/3.png"
        attribute joy_close:
            "layers/1.png"

image blink:
    "ushio_noa joy"
    pause 3
    "ushio_noa joy_close"
    pause 0.3
    repeat

transform noa_pos:
    pos(583,100)

label noa_blink:
    show blink at noa_pos
    return

#angry
transform angry:
    pos(775,250)
    zoom 0.3
    pause 0.1
    zoom 0.4
    pause 0.1
    zoom 0.3
    pause 0.1
    zoom 0.4
    pause 0.1

image emoji angry="images/emoji/angry.png"
label emoji_angry:
    show emoji angry at angry
    play sound "audio/emotion/angry.wav"
    return
#bulb
transform bulb:
    pos(825,325)
    anchor (1.0,1.0)
    zoom 0.3
    linear 0.1 zoom 0.4
    
image emoji bulb="images/emoji/bulb.png"
label emoji_bulb:
    show emoji bulb at bulb
    play sound "audio/emotion/bulb.wav"
    return

#chat
image emoji chat="images/emoji/Emoticon_Chat.png"
transform chat:
    ypos 400
    linear 0.1 rotate -15
    linear 0.1 rotate 15
    linear 0.1 rotate 15
    linear 0.1 rotate -15
    linear 0.1 rotate 15
    linear 0.1 rotate 15
label emoji_chat:
    show emoji chat at chat
    play sound "audio/emotion/SFX_Emoticon_Motion_Chat.wav"
    return 

#dot
image emoji dot1="images/emoji/Emoticon_Idea.png"
image emoji dot2="images/emoji/Emoticon_Balloon_N.png"
transform dot1:
    pos(725,250)
    zoom 0.5
transform dot2:
    pos(750,250)
    zoom 0.5
transform dot3:
    pos(775,250)
    zoom 0.5
label emoji_dot:
    show emoji dot2 at bulb
    pause 0.5
    play sound "audio/emotion/SFX_Emoticon_Motion_Dot.wav"
    show emoji dot1 as dot1 at dot1
    pause 0.5
    show emoji dot1 as dot2 at dot2
    pause 0.5
    show emoji dot1 as dot3 at dot3
    return

#exclaim
image emoji exclaim="images/emoji/Emoticon_ExclamationMark.png"
transform emoji_exclaim:
    pos(825,325)
    zoom 0
    rotate 0
    linear 0.1 zoom 0.45
label emoji_exclaim:
    show emoji exclaim at emoji_exclaim
    play sound "audio/emotion/SFX_Emoticon_Motion_Exclaim.wav"
    return

#heart
image emoji heart="images/emoji/Emoticon_Heart.png"
transform emoji_heart:
    pos(810,320)
    yzoom 0
    linear 0.1 yzoom 1
    linear 0.1 yzoom 0.8
    linear 0.1 yzoom 1
    linear 0.1 yzoom 0.8
    linear 0.1 yzoom 1

label emoji_heart:
    show emoji dot2 as basebulb behind emoji at bulb 
    show emoji heart at emoji_heart
    play sound "audio/emotion/SFX_Emoticon_Motion_Heart.wav"
    return

#music
image emoji music="images/emoji/Emoticon_Note.png"
transform emoji_music:
    pos(785, 235)
    zoom 0.3
    linear 0.1 xpos 783 ypos 232 zoom 0.5 rotate 5 
    linear 0.2 xpos 762 ypos 233 zoom 0.5 rotate -5 
    linear 0.1 xpos 754 ypos 234 rotate 5
    linear 0.2 xpos 750 rotate -5
    linear 0.1 xpos 740 rotate 5  
    linear 0.2 xpos 735
    linear 0.1 alpha 0 
    linear 0.2 xpos 745 zoom 0.5 rotate -5 
label emoji_music:
    show emoji music at emoji_music
    play sound "audio/emotion/SFX_Emoticon_Motion_Music.wav"
    return

#question
image emoji question="images/emoji/Emoticon_QuestionMark.png"
transform emoji_question:
    anchor (0.5,1.0)
    pos(775,300)
    zoom 0.3
    linear 0.2 zoom 0.5
label emoji_question:
    show emoji question at emoji_question
    play sound "audio/emotion/SFX_Emoticon_Motion_Question.wav"
    return

#respond
image emoji respond="images/emoji/Emoticon_Action.png"
transform emoji_respond:
    pos(765,325)
    pause 0.1
    alpha 0
    pause 0.1
    alpha 1
    pause 0.1
    alpha 0
label emoji_respond:
    show emoji respond at emoji_respond
    play sound "audio/emotion/SFX_Emoticon_Motion_Respond.wav"
    return

#sad
image emoji sad="images/emoji/Emoji_Sad.png"
transform emoji_sad:
    pos(750,225)
    zoom 0.6
    linear 0.3 ypos 275
label emoji_sad:
    show emoji sad at emoji_sad
    play sound "audio/emotion/SFX_Emoticon_Motion_Sad.wav"
    return

#shy
image emoji shy="images/emoji/Emoticon_Shy.png"
transform shy_base:
    pos(675,250)
    zoom 0.3
    linear 0.1 zoom 0.4
transform emoji_shy:
    zoom 0.4
    pos(725,285)
    anchor(0.5,0.5)
    linear 0.1 rotate -5
    linear 0.1 rotate 5
    linear 0.1 rotate 5
    linear 0.1 rotate -5
    linear 0.1 rotate 5
label emoji_shy:
    show emoji shy at emoji_shy
    show emoji dot2 as base at shy_base behind emoji
    play sound "audio/emotion/SFX_Emoticon_Motion_Shy.wav"
    return