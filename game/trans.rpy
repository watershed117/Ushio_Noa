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

image noa_blink:
    "ushio_noa joy"
    pause 3
    "ushio_noa joy_close"
    pause 0.3
    repeat

#angry
transform emoji_angry:
    pos(190,155)
    zoom 0.3
    pause 0.1
    zoom 0.4
    pause 0.1
    zoom 0.3
    pause 0.1
    zoom 0.4
    pause 0.1

image emoji angry="images/emoji/angry.png"

#bulb
transform emoji_bulb:
    pos(245,225)
    anchor (1.0,1.0)
    zoom 0.3
    linear 0.1 zoom 0.4
    
image emoji bulb="images/emoji/bulb.png"

#chat
image emoji chat="images/emoji/Emoticon_Chat.png"
transform emoji_chat:
    zoom 0.5
    pos(110,225)
    linear 0.1 rotate -15
    linear 0.1 rotate 15
    linear 0.1 rotate 15
    linear 0.1 rotate -15
    linear 0.1 rotate 15
    linear 0.1 rotate 15

#dot
image emoji dot1="images/emoji/Emoticon_Idea.png"
image emoji dot2="images/emoji/Emoticon_Balloon_N.png"
image dot:
    contains:
        pause 0.5
        "emoji dot1"
        pos(155,175)
        zoom 0.5
    contains:
        pause 1
        "emoji dot1"
        pos(180,175)
        zoom 0.5
    contains:
        pause 1.5
        "emoji dot1"
        pos(205,175)
        zoom 0.5

#exclaim
image emoji exclaim="images/emoji/Emoticon_ExclamationMark.png"
transform emoji_exclaim:
    anchor(0.5,1.0)
    pos(200,225)
    zoom 0
    rotate 0
    linear 0.1 zoom 0.45

#heart
image emoji heart="images/emoji/Emoticon_Heart.png"
transform emoji_heart:
    pos(165,160)
    zoom 0.5
    yzoom 0
    linear 0.1 yzoom 1
    linear 0.1 yzoom 0.8
    linear 0.1 yzoom 1
    linear 0.1 yzoom 0.8
    linear 0.1 yzoom 1

#music
image emoji music="images/emoji/Emoticon_Note.png"
transform emoji_music:
    # pos(785, 235)
    pos(220,150)
    zoom 0.3
    linear 0.1 xoffset -5 yoffset -3 zoom 0.5 rotate 5
    linear 0.2 xoffset -26 yoffset -2 zoom 0.5 rotate -5
    linear 0.1 xoffset -34 yoffset -1 rotate 5
    linear 0.2 xoffset -38 rotate -6
    linear 0.1 xoffset -48 rotate -1
    linear 0.2 xoffset -53
    linear 0.1 alpha 0
    
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
    pause 0.2
    alpha 0
    pause 0.2
    alpha 1
    pause 0.2
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

#sigh
image emoji sigh="images/emoji/Emoji_Sigh.png"
transform emoji_sigh:
    anchor(1.0,1.0)
    zoom 0.3
    pos(825,450)
    linear 0.1 zoom 0.5 xpos 800 ypos 475
label emoji_sigh:
    show emoji sigh at emoji_sigh
    play sound "audio/emotion/SFX_Emoticon_Motion_Sigh.wav"
    return

#steam
image emoji steam="images/emoji/Emoji_Steam.png"
transform emoji_steam:
    pos(750,350)
    zoom 0
    rotate -20
    linear 0.2 zoom 0.4
    linear 0.2 alpha 0
    alpha 1
    pos(750,300)
    zoom 0
    rotate 15
    linear 0.2 zoom 0.5
    linear 0.2 alpha 0
label emoji_steam:
    show emoji steam at emoji_steam
    play sound "audio/emotion/SFX_Emoticon_Motion_Steam.wav"
    return

#surprise
image emoji surprise1="images/emoji/Emoticon_Exclamation.png"
image emoji surprise2="images/emoji/Emoticon_Question.png"
transform emoji_surprise1:
    anchor(0.5,1.0)
    pos(790,325)
    xzoom 0.4
    yzoom 0
    linear 0.1 xzoom 0.5  yzoom 0.5 xoffset -50
transform emoji_surprise2:
    anchor(0.5,1.0)
    pos(825,325)
    xzoom 0.4
    yzoom 0
    linear 0.2 xzoom 0.5 yzoom 0.5 xoffset -50
label emoji_surprise:
    show emoji surprise1 as surprise1 at emoji_surprise1
    show emoji surprise2 as surprise2 at emoji_surprise2
    play sound "audio/emotion/SFX_Emoticon_Motion_Surprise.wav"
    return

#sweat
image emoji sweat="images/emoji/Emoticon_Sweat.png"
transform emoji_sweat:
    linear 0.3 yoffset -50
label emoji_sweat:
    show emoji sweat at truecenter zorder 999
    play sound "audio/emotion/SFX_Emoticon_Motion_Sweat.wav"
    return

#tear
image emoji tear1="images/emoji/Emoji_Tear_1.png"
image emoji tear2="images/emoji/Emoji_Tear_2.png"
transform emoji_tear1:
    anchor(1.0,1.0)
    pos(775,330)
    zoom 0
    linear 0.4 zoom 0.6
    linear 0.6 alpha 0
transform emoji_tear2:
    anchor(1.0,0.5)
    pos(775,270)
    zoom 0
    linear 0.4 zoom 0.7
    linear 0.6 alpha 0
label emoji_tear:
    show emoji tear2 as tear2 at emoji_tear2
    pause 0.1
    show emoji tear1 as tear1 at emoji_tear1
    play sound "audio/emotion/SFX_Emoticon_Motion_Tear.wav"
    return

#think
image emoji think0="images/emoji/Emoticon_Balloon_T.png"
image emoji think1="images/emoji/Emoticon_Ice_M.png"
image emoji think2="images/emoji/Emoticon_Ice_S.png"
image emoji think3="images/emoji/Emoticon_Ice_V.png"
transform emoji_think:
    anchor(1.0,1.0)
    pos(785,345)
    zoom 0
    linear 0.1 zoom 0.5
transform ice:
    anchor(0.5,0.5)
    pos(720,285)
    zoom 0
    linear 0.1 zoom 0.5
    linear 0.2 rotate -5
    linear 0.2 rotate 5
    linear 0.2 rotate -5
    linear 0.2 rotate 5
    linear 0.2 rotate -5
    linear 0.2 rotate 5
label emoji_think:
    show emoji think0 at emoji_think
    $ random_num = renpy.random.randint(1, 3)
    if random_num == 1:
        show  emoji think1 as ice at ice
    elif random_num == 2:
        show  emoji think2 as ice at ice
    else:
        show  emoji think1 as ice at ice
    play sound "audio/emotion/SFX_Emoticon_Motion_Think.wav"
    return

#twinkle
image emoji twinkle="images/emoji/Emoticon_Twinkle.png"
transform emoji_twinkle1:
    anchor(0.5,0.5)
    pos(740,290)
    zoom 0
    linear 0.3 zoom 0.5
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.5
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.5
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.5
    linear 0.2 alpha 0
transform emoji_twinkle2:
    anchor(0.5,0.5)
    pos(775,265)
    zoom 0
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.4
    linear 0.2 alpha 0
transform emoji_twinkle3:
    anchor(0.5,0.5)
    pos(775,315)
    zoom 0
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.2
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.2
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.2
    linear 0.3 zoom 0.3
    linear 0.2 alpha 0
label emoji_twinkle:
    show emoji twinkle as part1 at emoji_twinkle1
    show emoji twinkle as part2 at emoji_twinkle2
    show emoji twinkle as part3 at emoji_twinkle3
    play sound "audio/emotion/SFX_Emoticon_Motion_Twinkle.wav"
    return

#upset
image emoji upset="images/emoji/Emoticon_Anxiety.png"
transform emoji_upset:
    anchor(0.5,0.5)
    pos(720,290)
    zoom 0.55
    linear 0.1 rotate -5
    linear 0.1 rotate 5
    linear 0.1 rotate -5
    linear 0.1 rotate 5
    linear 0.1 rotate -5
    linear 0.1 rotate 5
    linear 0.1 rotate -5
    linear 0.1 rotate 5
label emoji_upset:
    show emoji dot2 as base at emoji_think
    show emoji upset at emoji_upset
    play sound "audio/emotion/SFX_Emoticon_Motion_Upset.wav"
    return

#zzz
image emoji zzz="images/emoji/Emoji_Zzz.png"
transform emoji_zzz1:
    anchor(0.5,0.5)
    pos(825,295)
    zoom 0.3
    rotate 15
transform emoji_zzz2:
    anchor(0.5,0.5)
    pos(795,280)
    zoom 0.4
transform emoji_zzz3:
    anchor(0.5,0.5)
    pos(765,300)
    zoom 0.5
    rotate -15
label emoji_zzz:
    play sound "audio/emotion/SFX_Emoticon_Motion_Zzz.wav"
    show emoji zzz as part1 at emoji_zzz1
    pause 0.5
    show emoji zzz as part2 at emoji_zzz2
    pause 0.5
    show emoji zzz as part3 at emoji_zzz3
    return