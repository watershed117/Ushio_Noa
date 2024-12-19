init 0 python:
    import os
    import json
    class Tools:
        def __init__(self):
            self.function_args_data={}
            self.function_args_data["control_character"]={"args":{"position":str,"emotion":str,"emoji":str,"action":str,"effect":str,"scaleup":str},"required":["position","emotion"]}
            self.function_args_data["bg_changer"]={"args":{"name":str},"required":["name"]}

        def dir_walker(self, path:str = os.path.join(renpy.config.gamedir,"images/background")):# C:\Users\water\Desktop\renpy\Ushio_Noa\game
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
            return dir_names+file_names

        def get_dirs(self,path:str=os.path.join(renpy.config.gamedir,"images/background")):
            dir_names=[]
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir():
                        dir_names.append(entry.name)
            return dir_names

        def control_character(self,position,emotion,emoji:str="",action=blank,effect=blank,scaleup=blank):
            if emoji:
                renpy.show_screen(emoji,position=position,emotion=emotion,action=action,effect=effect,scaleup=scaleup)
                renpy.store.tool_result.put({"control_character":"success"})
                # return "success"
            else:
                renpy.show_screen("noa_base",position=position,emotion=emotion,action=action,effect=effect,scaleup=scaleup)
                renpy.store.tool_result.put({"control_character":"success"})
                # return "success"
        
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
                    else:
                        renpy.store.tool_result.put({name:args_check})
                else:
                    renpy.store.tool_result.put({name:"is not callable"})
                if kwargs:
                    result=executor(**kwargs)
                else:
                    result=executor()
            else:
                renpy.store.tool_result.put({name:"function not found"})
            
    tools_caller = Tools()

label bg_changer(file_name):
    scene expression "images/background/"+file_name with dissolve
    return
