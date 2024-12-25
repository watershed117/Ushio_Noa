import requests
from io import BytesIO
import queue


class Audio_generator:
    def __init__(self,
                 #  gpt_path: str,
                 #  sovits_path: str,
                 port: int = 9880,
                 ) -> None:

        # self.gpt_path = gpt_path
        # self.sovits_path = sovits_path
        self.port = port

        self.event = queue.Queue()
        self.result = queue.Queue()
        self.ready = False

    def gen(self, text: str, language: str = "ja", refer_data: dict = {}, cut_method: str = "cut5"):
        """
        cut0: 不切
        cut1: 凑四句一切
        cut2: 凑50字一切
        cut3: 按中文句号。切
        cut4: 按英文句号.切
        cut5: 按标点符号切
        refer_data: {"refer_wav_path": "", "prompt_text": "", "prompt_language": ""}
        language and prompt_language:
        "all_zh",#全部按中文识别
        "en",#全部按英文识别#######不变
        "all_ja",#全部按日文识别
        "all_yue",#全部按中文识别
        "all_ko",#全部按韩文识别
        "zh",#按中英混合识别####不变
        "ja",#按日英混合识别####不变
        "yue",#按粤英混合识别####不变
        "ko",#按韩英混合识别####不变
        "auto",#多语种启动切分识别语种
        "auto_yue",#多语种启动切分识别语种


        """
        if text and refer_data:
            payload = {
                # str.(required) text to be synthesized
                "text": text,
                # str.(required) language of the text to be synthesized
                "text_lang": language,
                # str.(required) reference audio path
                "ref_audio_path": refer_data.get("refer_wav_path"),
                # list.(optional) auxiliary reference audio paths for multi-speaker synthesis
                "aux_ref_audio_paths": [],
                # str.(optional) prompt text for the reference audio
                "prompt_text": refer_data.get("prompt_text"),
                # str.(required) language of the prompt text for the reference audio
                "prompt_lang": refer_data.get("prompt_language"),
                "top_k": 5,                   # int. top k sampling
                "top_p": 1,                   # float. top p sampling
                "temperature": 1,             # float. temperature for sampling
                # str. text split method, see text_segmentation_method.py for details.
                "text_split_method": cut_method,
                "batch_size": 1,              # int. batch size for inference
                # float. threshold for batch splitting.
                "batch_threshold": 0.75,
                # bool. whether to split the batch into multiple buckets.
                "split_bucket": True,
                # bool. step by step return the audio fragment.
                "return_fragment": False,
                # float. control the speed of the synthesized audio.
                "speed_factor": 1.0,
                # bool. whether to return a streaming response.
                "streaming_mode": False,
                # int. random seed for reproducibility.
                "seed": -1,
                # bool. whether to use parallel inference.
                "parallel_infer": True,
                # float. repetition penalty for T2S model.
                "repetition_penalty": 1.35
            }
        else:
            pass  # todo: use bert to get emotion
        with requests.post(url=f"http://127.0.0.1:{self.port}/tts", json=payload) as response:
            if response.status_code == 200:
                audio = BytesIO()
                audio.write(response.content)
                audio.seek(0)
                # self.result.put(audio.getvalue())
                self.result.put(audio)
                self.ready = True
            else:
                self.result.put(response.json())
                self.ready = True

    def call_method(self, method_name: str, *args, **kwargs):
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                print(f"call method {method_name}")
                return method(*args, **kwargs)
            else:
                print(f"{method_name} not callable")
                return None
        else:
            print(f"{method_name} not found")
            return None

    def process_event(self, event):
        """
        处理事件，根据事件类型调用相应的方法。

        参数:
            event: 可以是字符串（方法名）或元组 (method_name, args, kwargs)。

        返回:
            方法调用的结果或 None。
        """
        if isinstance(event, str):  # 事件是一个方法名字符串
            return self.call_method(event)
        elif isinstance(event, tuple) and len(event) > 0:  # 事件是一个元组
            method_name = event[0]  # 第一个元素是方法名
            if len(event) == 1:  # 只有方法名，无参数
                return self.call_method(method_name)
            elif len(event) == 2:  # 方法名和参数
                if isinstance(event[1], dict):  # 第二个元素是字典，作为 kwargs 处理
                    return self.call_method(method_name, **event[1])
                elif isinstance(event[1], tuple):  # 第二个元素是元组，作为 args 处理
                    return self.call_method(method_name, *event[1])
            elif len(event) == 3:  # 方法名、args 和 kwargs
                args = event[1] if isinstance(event[1], tuple) else ()
                kwargs = event[2] if isinstance(event[2], dict) else {}
                return self.call_method(method_name, *args, **kwargs)
        return None

    def run(self):
        while True:
            event = self.event.get()
            if event:
                self.process_event(event)


if __name__ == "__main__":
    import sounddevice as sd
    import soundfile as sf
    import threading
    import time

    generator = Audio_generator(port=9880)
    t = threading.Thread(target=generator.run)
    t.start()
    refer_data = {"refer_wav_path": r"D:\GPT-SoVITS-v2-240821\GPT-SoVITS-v2-240821\output\noa\noa_153.wav",
                  "prompt_text": "それならゆうかちゃんの声が流れる目覚まし時計とかいいかもしれませんね",
                  "prompt_language": "ja"}
    generator.event.put(
        ("gen", {"text": "こんにちは、どういたしまして？", "language": "ja", "refer_data": refer_data}))
    while not generator.ready:
        time.sleep(0.1)
    generator.ready = False
    audio = generator.result.get()
    data, samplerate = sf.read(audio)
    sd.play(data, samplerate)
    sd.wait()
