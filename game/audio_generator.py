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

    def gen(self, text: str, language: str = "all_ja", refer_data: dict = {}, cut_method: str = "cut3"):
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
                return audio
            else:
                return response.json()

    def exit(self):
        try:
            with requests.get(url=f"http://127.0.0.1:{self.port}/exit") as response:
                pass
        except:
            pass