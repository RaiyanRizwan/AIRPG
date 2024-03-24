import openai
import time
from typing import List, Dict
import numpy as np

class GPTEndpoint:
    
    def __init__(self, API_KEY: str, limit_call_frequency: bool = False, call_cooldown: float = 10) -> None:
        self.api_key = API_KEY
        self.call_cooldown = call_cooldown # seconds
        self.last_call_timestamp = -self.call_cooldown
        self.limit_call_frequency = limit_call_frequency

    def complete(self, message_stream: List[Dict], model: str) -> str:
        if self.limit_call_frequency and time.time() - self.last_call_timestamp < self.call_cooldown:
            return "Too many calls too fast."
        openai.api_key = self.api_key
        output = openai.chat.completions.create(
            model=model,
            messages=message_stream
        ).choices[0].message.content
        self.last_call_timestamp = time.time()
        return output
    
    def embedding(self, texts:List[str], dimensions: int, model:str="text-embedding-3-small") -> np.ndarray:
        if self.limit_call_frequency and time.time() - self.last_call_timestamp < self.call_cooldown:
            return "Too many calls too fast."
        processed_texts = [text.replace("\n", " ") for text in texts]
        response = openai.embeddings.create(input=processed_texts, model=model, dimensions=dimensions)
        self.last_call_timestamp = time.time()
        return np.array([np.array(item.embedding) for item in response.data])
