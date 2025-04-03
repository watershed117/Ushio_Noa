from typing import Callable
import requests
from requests.exceptions import HTTPError,RequestException,ConnectionError,Timeout

class RAG_Client:
    def __init__(self, base_url:str):
        self.base_url = base_url
        self.client = requests.Session()


    def handle_requests(self, func:Callable, *args, **kwargs)->requests.Response:
        try:
            response = func(*args, **kwargs)
        except Timeout:
            raise Timeout("Request timed out")
        except ConnectionError:
            raise ConnectionError("Error connecting to server")
        except RequestException as e:
            raise e
        except Exception as e:
            raise e
        if response.status_code == 200:
            return response
        else:
            raise HTTPError(f"Error: {response.status_code} - {response.text}")
        
    def create_collection(self, collection_name:str,metadata:dict={}):
        url = f"{self.base_url}/rag/create_collection/{collection_name}"
        if metadata:
            data = {"metadata":metadata}
            handle_requests = self.handle_requests(self.client.get, url,json=data)
        else:
            handle_requests = self.handle_requests(self.client.get, url)
        return handle_requests.json()
    
    def delete_collection(self, collection_name:str):
        url = f"{self.base_url}/rag/delete_collection/{collection_name}"
        handle_requests = self.handle_requests(self.client.get, url)
        return handle_requests.json()
    
    def change_collection(self, collection_name:str):
        url = f"{self.base_url}/rag/change_collection/{collection_name}"
        handle_requests = self.handle_requests(self.client.get, url)
        return handle_requests.json()
    
    def store(self, text:str, metadata:dict[str,str]={}):
        url = f"{self.base_url}/rag/store"
        data = {"text":text, "metadata":metadata}
        print(data)
        handle_requests = self.handle_requests(self.client.post, url, json=data)
        return handle_requests.json()
    
    def query(self, query_text:str, top_k:int=1):
        url = f"{self.base_url}/rag/query"
        data = {"query_text":query_text, "top_k":top_k}
        handle_requests = self.handle_requests(self.client.post, url, json=data)
        result = handle_requests.json().get("result")
        for i in result:
            if i:
                pass
            else:
                raise ValueError("No result found")
        documents = result[0][0]  # 提取文档列表（如 ['doc1', 'doc2', 'doc3']）
        metadatas = result[1][0]  # 提取元数据列表（如 [{'title': '...'}, {'title': '...'}, ...]）
        ids = result[2][0]        # 提取ID列表（如 ['id1', 'id2', 'id3']）
        distances = result[3][0]  
        
        formatted_data = []
        for doc, meta, id_, distance in zip(documents, metadatas, ids, distances):
            formatted_data.append({
                "document": doc,
                "metadata": meta,
                "id": id_,
                "distance": distance
            })
        
        return formatted_data

    
    def update(self, id:str, text:str, metadata:dict[str,str]={}):
        url = f"{self.base_url}/rag/update"
        data = {"id":id, "text":text, "metadata":metadata}
        handle_requests = self.handle_requests(self.client.post, url, json=data)
        return handle_requests.json()
    
    def delete(self, id:str):
        url = f"{self.base_url}/rag/delete"
        data = {"id":id}
        handle_requests = self.handle_requests(self.client.post, url, json=data)
        return handle_requests.json()
    
    def release_disk(self, collection_name:str):
        url = f"{self.base_url}/rag/release_disk/{collection_name}"
        handle_requests = self.handle_requests(self.client.get, url)
        return handle_requests.json()
    
if __name__ == "__main__":
    rag=RAG_Client("http://localhost:20000")
    # result=rag.create_collection("test_collection", {
    #     "hnsw:space": "cosine",
    #     "hnsw:search_ef": 100
    # })
    # print(result)
    result=rag.change_collection("test_collection")
    print(result)
    result=rag.store("近年来，基于注意力机制的Transformer架构在自然语言处理领域取得了突破性进展。以BERT、GPT-3为代表的大规模预训练模型通过自监督学习，显著提升了文本生成、问答和翻译任务的性能。然而，这类模型的计算资源消耗极大（如GPT-3训练需1750亿参数），引发了关于能效比和可解释性的争议。本文提出了一种动态稀疏化训练方法，在保持模型精度的同时减少30%的计算开销。")
    print(result)
    result=rag.store("通过对CRISPR-Cas9基因编辑系统的优化，本研究成功在小鼠模型中修复了导致囊性纤维化的CFTR基因突变。实验组（n=50）的肺部组织病理学评分较对照组（n=50）显著改善（p<0.01），且未观察到脱靶效应。进一步RNA测序分析表明，修复后的基因表达谱与健康组高度一致（Pearson r=0.92）。")
    print(result)
    result=rag.store("根据《通用数据保护条例》（GDPR）第17条，用户有权要求删除其个人数据。若您希望行使此权利，需通过书面申请提交至数据保护官（DPO），并提供有效身份证明。平台将在30个工作日内完成核查，若数据不涉及法定保留情形（如交易记录需保存5年），将永久删除相关数据并发送确认通知。请注意，删除后可能影响部分服务的正常使用。")
    print(result)
    result=rag.store("本发明涉及一种基于区块链的供应链溯源方法，其特征在于：1）将商品生产、运输、销售各环节数据上链，生成不可篡改的时间戳哈希；2）通过零知识证明技术实现敏感数据（如供应商价格）的隐私保护；3）支持消费者通过扫码验证商品全生命周期信息。实施例显示，该系统可降低80%的伪劣商品流通风险。")
    print(result)
    result=rag.query("基因编辑", 10)
    print(result)
    result=rag.delete_collection("test_collection")
    print(result)