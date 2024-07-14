import requests
from io import BytesIO
import queue

class Auduio_generator:
    def __init__(self,
                 #  gpt_path: str,
                 #  sovits_path: str,
                 port: int = 9880,
                 ) -> None:

        # self.gpt_path = gpt_path
        # self.sovits_path = sovits_path
        self.port = port

        self.event_queue = queue.Queue()

        self.gen_ready=False
        self.gen_output=None

    def gen(self, text: str, language: str = "ja", path: str = None, refer_data: dict = None,):
        if refer_data:
            playload = {
                "refer_wav_path": refer_data.get("refer_wav_path"),
                "prompt_text": refer_data.get("prompt_text"),
                "prompt_language": refer_data.get("prompt_language"),
                "text": text,
                "text_language": language
            }
        else:
            playload = {"text": text,
                        "text_language": language}
        with requests.post(url=f"http://127.0.0.1:{self.port}", stream=True, json=playload) as response:
            if response.status_code == 200:
                if path:
                    with open(path, "wb+") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    self.gen_output=None
                    self.gen_ready=True
                else:
                    audio = BytesIO()
                    for chunk in response.iter_content(chunk_size=8192):
                        audio.write(chunk)
                    self.gen_output=audio.getvalue()
                    self.gen_ready=True
                    audio.seek(0)#del 
                    return audio#del
            else:
                print(response.json())

    # def set_model(self, gpt_path: str, sovits_path: str):
    #     with requests.post(url=f"http://127.0.0.1:{self.port}/set_model", json={"gpt_model_path": gpt_path,
    #                                                                             "sovits_model_path": sovits_path}) as response:
    #         if response.status_code == 200:
    #             print("ok")
    #         else:
    #             print(response.status_code)

    def change_refer(self, refer_audio: str, refer_text: str, refer_language: str = "ja"):
        with requests.post(url=f"http://127.0.0.1:{self.port}/change_refer", json={"refer_wav_path": refer_audio,
                                                                                   "prompt_text": refer_text,
                                                                                   "prompt_language": refer_language}) as response:
            if response.status_code == 200:
                print("ok")
            else:
                print(response.status_code)

    def run(self):
        while True:
            event = self.event_queue.get()
            function_name = list(event.keys())[0]
            method = getattr(self, function_name, None)
            method(*event[function_name])

if __name__=="__main__":
    import sounddevice as sd
    import soundfile as sf

    generator=Auduio_generator(port=9880)
    audio=generator.gen("こんにちは、どういたしまして？","ja")
    # generator.gen("こんにちは、どういたしまして？","ja",r"C:\Users\water\Downloads\tmp.wav")
    data, samplerate = sf.read(audio)
    sd.play(data,samplerate)
    sd.wait()