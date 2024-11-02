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
image emoji dot:
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
    pos(220,150)
    zoom 0.3
    linear 0.1 xoffset -5 yoffset -3 zoom 0.5 rotate 5
    linear 0.2 xoffset -26 yoffset -2 zoom 0.5 rotate -5
    linear 0.1 xoffset -34 yoffset -1 rotate 5
    linear 0.2 xoffset -38 rotate -6
    linear 0.1 xoffset -48 rotate -1
    linear 0.2 xoffset -53
    # linear 0.1 alpha 0

#question
image emoji question="images/emoji/Emoticon_QuestionMark.png"
transform emoji_question:
    anchor (0.5,1.0)
    pos(200,225)
    zoom 0.3
    linear 0.2 zoom 0.5

#respond
image emoji respond="images/emoji/Emoticon_Action.png"
transform emoji_respond:
    pos(150,150)
    zoom 0.5
    pause 0.2
    alpha 0
    pause 0.2
    alpha 1
    pause 0.2
    # alpha 0

#sad
image emoji sad="images/emoji/Emoji_Sad.png"
transform emoji_sad:
    pos(175,125)
    zoom 0.6
    linear 0.3 yoffset 50

#shy
image emoji shy="images/emoji/Emoticon_Shy.png"
transform shy_base:
    pos(100,175)
    zoom 0.3
    linear 0.1 zoom 0.4
transform emoji_shy:
    zoom 0.4
    pos(150,210)
    anchor(0.5,0.5)
    linear 0.1 rotate -5
    linear 0.1 rotate 5
    linear 0.1 rotate 5
    linear 0.1 rotate -5
    linear 0.1 rotate 5

#sigh
image emoji sigh="images/emoji/Emoji_Sigh.png"
transform emoji_sigh:
    anchor(1.0,1.0)
    zoom 0.3
    pos(225,330)
    linear 0.1 zoom 0.5 xoffset -25 yoffset 25

#steam
image emoji steam="images/emoji/Emoji_Steam.png"
transform emoji_steam:
    anchor(1.0,1.0)
    pos(175,250)
    zoom 0
    rotate -20
    linear 0.2 zoom 0.4
    linear 0.2 alpha 0
    alpha 1
    pos(175,200)
    zoom 0
    rotate 15
    linear 0.2 zoom 0.5
    # linear 0.2 alpha 0

#surprise
image emoji surprise1="images/emoji/Emoticon_Exclamation.png"
image emoji surprise2="images/emoji/Emoticon_Question.png"
transform emoji_surprise1:
    anchor(0.5,1.0)
    pos(210,225)
    xzoom 0.4
    yzoom 0
    linear 0.1 xzoom 0.5  yzoom 0.5 xoffset -50
transform emoji_surprise2:
    anchor(0.5,1.0)
    pos(245,225)
    xzoom 0.4
    yzoom 0
    linear 0.2 xzoom 0.5 yzoom 0.5 xoffset -50

#sweat
image emoji sweat="images/emoji/Emoticon_Sweat.png"
transform emoji_sweat:
    zoom 0.5
    pos(215,95)
    linear 0.3 yoffset 60

#tear
image emoji tear1="images/emoji/Emoji_Tear_1.png"
image emoji tear2="images/emoji/Emoji_Tear_2.png"
image emoji tear:
    contains:
        "emoji tear2"
        anchor(1.0,0.5)
        pos(190,180)
        zoom 0
        linear 0.4 zoom 0.7
        # linear 0.6 alpha 0
    contains:
        "emoji tear1"
        anchor(1.0,0.0)
        pos(190,185)
        zoom 0
        pause 0.1
        linear 0.4 zoom 0.6
        # linear 0.6 alpha 0

#think
image emoji think0="images/emoji/Emoticon_Balloon_T.png"
image emoji think1="images/emoji/Emoticon_Ice_M.png"
image emoji think2="images/emoji/Emoticon_Ice_S.png"
image emoji think3="images/emoji/Emoticon_Ice_V.png"
transform emoji_think:
    anchor(1.0,1.0)
    pos(200,250)
    zoom 0
    linear 0.1 zoom 0.5
transform ice:
    anchor(0.5,0.5)
    pos(135,190)
    zoom 0
    linear 0.1 zoom 0.5
    linear 0.2 rotate -5
    linear 0.2 rotate 5
    linear 0.2 rotate -5
    linear 0.2 rotate 5
    linear 0.2 rotate -5
    linear 0.2 rotate 5

#twinkle
image emoji twinkle="images/emoji/Emoticon_Twinkle.png"
transform emoji_twinkle1:
    anchor(0.5,0.5)
    pos(175,175)
    zoom 0
    linear 0.3 zoom 0.5
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.5
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.5
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.5
    # linear 0.2 alpha 0
transform emoji_twinkle2:
    anchor(0.5,0.5)
    pos(210,150)
    zoom 0
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.4
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.4
    # linear 0.2 alpha 0
transform emoji_twinkle3:
    anchor(0.5,0.5)
    pos(210,200)
    zoom 0
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.2
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.2
    linear 0.3 zoom 0.3
    linear 0.2 zoom 0.2
    linear 0.3 zoom 0.3
    # linear 0.2 alpha 0

#upset
image emoji upset="images/emoji/Emoticon_Anxiety.png"
transform emoji_upset:
    anchor(0.5,0.5)
    pos(135,195)
    zoom 0.55
    linear 0.1 rotate -5
    linear 0.1 rotate 5
    linear 0.1 rotate -5
    linear 0.1 rotate 5
    linear 0.1 rotate -5
    linear 0.1 rotate 5
    linear 0.1 rotate -5
    linear 0.1 rotate 5

#zzz
image emoji zzz1="images/emoji/Emoji_Zzz.png"
image emoji zzz:
    contains:
        "emoji zzz1"
        anchor(0.5,0.5)
        # pos(825,295)
        pos(245,190)
        zoom 0.3
        rotate 15
    contains:
        pause 0.5
        "emoji zzz1"
        anchor(0.5,0.5)
        # pos(795,280)
        pos(215,180)
        zoom 0.4
    contains:
        pause 1.0
        "emoji zzz1"
        anchor(0.5,0.5)
        # pos(765,300)
        pos(185,200)
        zoom 0.5
        rotate -15