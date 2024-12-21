init 0 python:
    import os
    import json
    from typing import Any
    class Tools:
        def __init__(self):
            self.function_args_data={}
            self.map_data={}

            self.args_register("dir_walker", {"path": str}, ["path"])
            self.args_register("control_character", {"position": str, "emotion": str, "emoji": str, "action": str, "effect": str, "scaleup": str}, ["position", "emotion"])
            self.args_register("bg_changer", {"name": str}, ["name"])

            self.map_register("control_character",
                            {
                            "position": {"1":"1",
                                        "2":"2",
                                        "3":"3",
                                        "4":"4",
                                        "5":"5"},
                            "emotion": {"joy":"joy",
                                        "sadness":"sadness",
                                        "anger":"anger",
                                        "surprise":"surprise",
                                        "fear":"fear",
                                        "disgust":"disgust",
                                        "embarrassed":"embarrassed",
                                        "normal":"normal"},
                            "emoji":  { "angry":"angry",
                                        "bulb":"bulb",
                                        "chat":"chat",
                                        "dot":"dot",
                                        "exclaim": "exclaim",
                                        "heart":"heart",
                                        "music":"music",
                                        "question":"question",
                                        "respond":"respond",
                                        "sad":"sad",
                                        "shy":"shy",
                                        "sigh":"sigh",
                                        "steam":"steam",
                                        "surprise":"surprise",
                                        "sweat":"sweat",
                                        "tear":"tear",
                                        "think":"think",
                                        "twinkle":"twinkle",
                                        "upset":"upset",
                                        "zzz":"zzz"},
                            "action": { "blank":blank,
                                        "sightly_down":sightly_down,
                                        "fall_left":fall_left,
                                        "fall_right":fall_right,
                                        "jump":jump,
                                        "jump_more":jump_more,
                                        "shake":shake,
                                        "shake_more":shake_more},
                            "effect": { "blank":blank,
                                        "hide":"hide",
                                        "holography":"holography"},
                            "scaleup": {"blank":blank,
                                        "scaleup":scaleup}
                                        })

        def map_register(self,name:str,map_data:dict):
            self.map_data[name]=map_data

        def control_character(self,
                            position: str,
                            emotion: str, 
                            emoji: str = "", 
                            action: str = "blank", 
                            effect: str = "blank", 
                            scaleup: str = "blank"):
            error_message=[]

            if position not in self.map_data["control_character"]["position"]:
                error_message.append(f"position {position} not found")
            else:
                position=self.map_data["control_character"]["position"][position]

            if emotion not in self.map_data["control_character"]["emotion"]:
                error_message.append(f"emotion {emotion} not found")
            else:
                emotion=self.map_data["control_character"]["emotion"][emotion]

            if emoji:
                if emoji not in self.map_data["control_character"]["emoji"]:
                    error_message.append(f"emoji {emoji} not found")
                else:
                    emoji=self.map_data["control_character"]["emoji"][emoji]

            if action not in self.map_data["control_character"]["action"]:
                error_message.append(f"action {action} not found")
            else:
                action=self.map_data["control_character"]["action"][action]

            if effect not in self.map_data["control_character"]["effect"]:
                error_message.append(f"effect {effect} not found")
            else:
                effect=self.map_data["control_character"]["effect"][effect]

            if scaleup not in self.map_data["control_character"]["scaleup"]:
                error_message.append(f"scaleup {scaleup} not found")
            else:
                scaleup=self.map_data["control_character"]["scaleup"][scaleup]

            if error_message:
                renpy.store.tool_result.put({"control_character": error_message})
            else:
                if emoji:
                    renpy.show_screen(emoji, position=position, emotion=emotion,
                                    action=action, effect=effect, scaleup=scaleup)
                    renpy.store.tool_result.put({"control_character": "success"})
                else:
                    renpy.show_screen("noa_base", position=position, emotion=emotion,
                                    action=action, effect=effect, scaleup=scaleup)
                    renpy.store.tool_result.put({"control_character": "success"})
        
        def bg_changer(self,name:str):
            if renpy.loadable("images/background/"+name):
                renpy.store.tool_result.put({"name":"bg_changer","result":"success"})
            else:
                renpy.store.tool_result.put({"name":"bg_changer","result":"file not found"})
            renpy.call("bg_changer",name)
            return "success" # cannot return "success"

        def args_register(self,name:str,args:dict[str,type],required:list[str]):
            self.function_args_data[name]={"args":args,"required":required}

        def args_check(self,name:str,args:dict):
            if name not in self.function_args_data:
                raise ValueError(f"function {name}'s arguments are not registered")
            missed_required=[]
            type_error_args=[]
            unexpected_args=[]
            for r in self.function_args_data[name]["required"]:
                if r not in args:
                    missed_required.append(r)
            for k,v in args.items():
                if k not in self.function_args_data[name]["args"]:
                    unexpected_args.append(k)
                if not isinstance(v,self.function_args_data[name]["args"][k]):
                    type_error_args.append(k)

            args_error=[]
            if len(missed_required)>0:
                args_error.append(f"missing required arguments: {missed_required}")
            if len(unexpected_args)>0:
                args_error.append(f"unexpected arguments: {unexpected_args}")
            if len(type_error_args)>0:
                args_error.append(f"argument type error: {type_error_args}")
            if len(args_error)>0:
                error_message=",".join(args_error)
                return error_message
            else:
                return True

        def caller(self,function_data:str):
            name=function_data.get("name")
            kwargs=json.loads(function_data.get("arguments"))
            if hasattr(self, name):
                if callable(getattr(self,name)):
                    args_check=self.args_check(name,kwargs)
                    if args_check is True:
                        executor=getattr(self,name)
                        if kwargs:
                            result=executor(**kwargs)
                        else:
                            result=executor()
                    else:
                        renpy.store.tool_result.put({name:args_check})
                else:
                    renpy.store.tool_result.put({name:"is not callable"})
            else:
                renpy.store.tool_result.put({name:"function not found"})

        def dir_walker(self, path:str):
            background_path=os.path.join(renpy.config.gamedir,"images/background")
            # C:\Users\water\Desktop\renpy\Ushio_Noa\game\images\background
            path=os.path.join(background_path,path)
            if not os.path.exists(path):
                renpy.store.tool_result.put({"dir_walker": "dir not found"})
            else:
                dir_names=[]
                file_names=[]
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_file():
                            if entry.name == "desktop.ini":
                                pass
                            else:
                                file_names.append(entry.name)
                        elif entry.is_dir():
                            dir_names.append(entry.name)
                renpy.store.tool_result.put({"dir_walker": file_names})

        def get_dirs(self,path:str=os.path.join(renpy.config.gamedir,"images/background")):
            dir_names=[]
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir():
                        dir_names.append(entry.name)
            return dir_names

    tools_caller = Tools()

label bg_changer(file_name):
    scene expression "images/background/"+file_name with dissolve
    return
