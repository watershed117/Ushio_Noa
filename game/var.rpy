default position_map={
    "1": (0, 200),
    "2": (300, 200),
    "3": (600, 200),
    "4": (900, 200),
    "5": (1200, 200)
}

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


default new_conversation=False
default conversation_id=""
default tool_call_counts={"control_character":0,"bg_changer":0}


default tts_audio=None
default tts_filename=""

default run_in_main_context=["bg_changer","control_character"]