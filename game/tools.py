import os

class Tools:
    def __init__(self):
        pass

    def dir_walker(self, path:str):# C:\Users\water\Desktop\renpy\Ushio_Noa\game
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

    def get_dirs(self,path:str)->list[str]:
        dir_names=[]
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    dir_names.append(entry.name)
        return dir_names
if  __name__ == "__main__":
    tools=Tools()
    result=tools.dir_walker(r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\images\background\park")
    print(result)