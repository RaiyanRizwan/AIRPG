import openai
import time
from typing import List, Dict
import numpy as np

class GPTEndpoint:
    
    def __init__(self, API_KEY: str, call_cooldown: float = 10) -> None:
        self.api_key = API_KEY
        self.call_cooldown = call_cooldown # seconds
        self.last_call_timestamp = -self.call_cooldown

    def complete(self, message_stream: List[Dict], model: str) -> str:
        if time.time() - self.last_call_timestamp < self.call_cooldown:
            return "Too many calls too fast."
        openai.api_key = self.api_key
        output = openai.ChatCompletion.create(
            model=model,
            messages=message_stream
        ).choices[0].message['content']
        self.last_call_timestamp = time.time()
        return output
    
    def embedding(self, texts:List[str], dimensions: int, model:str="text-embedding-3-small"):
        if time.time() - self.last_call_timestamp < self.call_cooldown:
            return "Too many calls too fast."
        processed_texts = [text.replace("\n", " ") for text in texts]
        response = openai.embeddings.create(input=processed_texts, model=model, dimensions=dimensions).data[0].embedding
        self.last_call_timestamp = time.time()
        return np.array([np.array(item['embedding']) for item in response['data']])
