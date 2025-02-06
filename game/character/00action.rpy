transform sightly_down:
    ease 0.2 yoffset 100
    pause 0.1
    ease 0.2 yoffset 0

transform fall_left:
    rotate_pad False
    easein 0.4 rotate -15
    easein 0.4 rotate 5
    easeout 0.3 rotate -15 yoffset 800
    ease 0.3 rotate 0 yoffset 0

transform fall_right:
    rotate_pad False
    easein 0.4 rotate 15
    easein 0.4 rotate -5
    easeout 0.3 rotate 15 yoffset 800
    ease 0.3 rotate 0 yoffset 0

transform jump_more:
    ease 0.1 yoffset -100
    ease 0.1 yoffset 0
    ease 0.1 yoffset -100
    ease 0.1 yoffset 0

transform jump:
    ease 0.1 yoffset -100
    ease 0.1 yoffset 0

transform shake:
    linear 0.05 xoffset 10
    linear 0.05 xoffset -10
    linear 0.05 xoffset 10
    linear 0.05 xoffset -10
    linear 0.05 xoffset 0
    linear 0.05 xoffset 10
    linear 0.05 xoffset -10
    linear 0.05 xoffset 10
    linear 0.05 xoffset -10
    linear 0.05 xoffset 0

transform shake_more:
    linear 0.05 xoffset 20
    linear 0.05 xoffset -20
    linear 0.05 xoffset 0