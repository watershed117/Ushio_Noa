from api_ver import Gemini, GEMINI, MessageGenerator, HTTPException
import os
import json
import time


class Multimodal_Processor(Gemini):
    def __init__(self,
                 api_key: str,
                 base_url: str = "https://open.bigmodel.cn/api/paas/v4",
                 model: str = "glm-4-flash",
                 storage: str = "",
                 tools: list = [],
                 system_prompt: str = "",
                 limit: str = "128k",
                 proxy: dict = {
                     'http': 'http://127.0.0.1:7890',
                     'https': 'http://127.0.0.1:7890',
                 },
                 ffmpeg_path: str = "ffmpeg"
                 ):
        super().__init__(api_key, base_url, model,
                         storage, tools, system_prompt, limit, proxy)
        self.message_generator = MessageGenerator(
            file_format=GEMINI, ffmpeg_path=ffmpeg_path)

    def process_message(self, message: str, file_path: list[str]):
        data = self.send(
            self.message_generator.gen_user_msg(message, file_path))
        self.clear_history()
        return data

    def find_files_with_extension(self, dir_path, file_extension):
        """
        遍历指定文件夹及其子文件夹，查找指定格式的文件。

        参数:
            dir_path (str): 要遍历的文件夹路径。
            file_extension (str): 目标文件的扩展名（例如 ".txt" 或 "txt"）。

        返回:
            list: 匹配的文件路径列表。
        """
        result = []
        # 统一处理文件扩展名，确保以 . 开头
        target_extension = file_extension.strip('.')

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                # 获取文件的完整路径
                file_path = os.path.join(root, file)
                # 获取文件的扩展名
                _, ext = os.path.splitext(file)
                if ext.lstrip('.') == target_extension:
                    result.append(file_path)

        return result


chat = Multimodal_Processor(base_url="https://gemini.watershed.ip-ddns.com/v1",
                            model="gemini-2.0-flash-exp",
                            api_key="AIzaSyAv6RumkrxIvjLKgtiE-UceQODvvbTMd0Q",
                            storage=r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\history",
                            system_prompt="使用中文回复",
                            proxy=None,)  # type: ignore
# models = chat.list_models()
# with open(r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\gemini_models.json", "w", encoding="utf-8") as f:
#     json.dump(models, f, ensure_ascii=False, indent=4)

# del models

file_list = chat.find_files_with_extension(
    r"C:\Users\water\Desktop\renpy\Ushio_Noa\game\images\background", ".jpg")
print(len(file_list))
error_list = []
def process_file(file):
    for file in file_list:
        try:
            data = chat.process_message(f"使用中文描述图片内的信息", [file])
        except HTTPException as e:
            error_list.append(file)
            print(f"Error: {file} http status code: {e.status_code}")
            if e.status_code == 429:
                print("Too many requests, waiting for 60 seconds...")
                time.sleep(60)
            continue
        except Exception as e:
            error_list.append(file)
            print(f"Error: {file} {e}")
            continue

        file_path = os.path.dirname(file)
        file_name = os.path.basename(file)
        file_name = file_name.split(".")[0]
        with open(os.path.join(file_path, f"{file_name}.txt"), "w", encoding="utf-8") as f:
            f.write(data["content"])

        print(f"Processed: {file}")

start = time.time()
while True:
    process_file(file_list)
    if not error_list:
        break
    file_list = error_list
    error_list = []

over = time.time()
print(f"Processed all files in {over-start:.2f} seconds.")