from api_ver import Base_llm

class DeepSeek(Base_llm):
    def __init__(self, api_key: str,
                 model: str = "deepseek-chat",
                 storage: str = "",
                 tools: list = [],
                 system_prompt: str = "",
                 limit: str = "128k",
                 proxy: dict = {
                     'http': 'http://127.0.0.1:7890',
                     'https': 'http://127.0.0.1:7890',
                 }
                 ):
        super().__init__(base_url="https://api.deepseek.com", api_key=api_key, model=model, storage=storage,
                         tools=tools, system_prompt=system_prompt, limit=limit, proxy=proxy)

    @Base_llm.result_appender  # type: ignore
    def list_models(self):
        url = f"{self.base_url}/models"
        response = self.client.get(url, proxies=self.proxy)
        if response.status_code == 200:
            result = response.json()
            return result.get("data")
        else:
            return response.status_code, response.json()




if __name__ == '__main__':
    api_key = "sk-63bcccdd316243aeac4e8cc5fcf5d8a1"

    deepseek=DeepSeek(api_key=api_key,
                      limit="8k",
                      proxy=None) # type: ignore

    # result = deepseek.list_models()
    # print(result)
    result = deepseek.send({"role": "user", "content": "你好"})
    print(result)