from typing import Callable
import requests
from requests.exceptions import HTTPError,RequestException,ConnectionError,Timeout

class RAG_Client:
    def __init__(self, base_url:str):
        self.base_url = base_url
        self.client = requests.Session()


    def handel_requests(self, func:Callable, *args, **kwargs)->requests.Response:
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
    def create_collection(self, collection_name:str):
        url = f"{self.base_url}/rag/create_collection/{collection_name}"
        handle_requests = self.handel_requests(self.client.get, url)
        return handle_requests.json()
    
    def delete_collection(self, collection_name:str):
        url = f"{self.base_url}/rag/delete_collection/{collection_name}"
        handle_requests = self.handel_requests(self.client.get, url)
        return handle_requests.json()
    
    def change_collection(self, collection_name:str):
        url = f"{self.base_url}/rag/change_collection/{collection_name}"
        handle_requests = self.handel_requests(self.client.get, url)
        return handle_requests.json()
    
    def store(self, text:str, metadata:dict[str,str]={}):
        url = f"{self.base_url}/rag/store"
        data = {"text":text, "metadata":metadata}
        handle_requests = self.handel_requests(self.client.post, url, json=data)
        return handle_requests.json()
    
    def query(self, query_text:str, top_k:int=1):
        url = f"{self.base_url}/rag/query"
        data = {"query_text":query_text, "top_k":top_k}
        handle_requests = self.handel_requests(self.client.post, url, json=data)
        return handle_requests.json()
    
    def update(self, id:str, text:str, metadata:dict[str,str]={}):
        url = f"{self.base_url}/rag/update"
        data = {"id":id, "text":text, "metadata":metadata}
        handle_requests = self.handel_requests(self.client.post, url, json=data)
        return handle_requests.json()
    
    def delete(self, id:str):
        url = f"{self.base_url}/rag/delete"
        data = {"id":id}
        handle_requests = self.handel_requests(self.client.post, url, json=data)
        return handle_requests.json()
    
    def release_disk(self, collection_name:str):
        url = f"{self.base_url}/rag/release_disk/{collection_name}"
        handle_requests = self.handel_requests(self.client.get, url)
        return handle_requests.json()