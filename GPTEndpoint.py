import openai
import time
from typing import List, Dict

class GPTEndpoint:
    
    def __init__(self, API_KEY: str, call_cooldown: float = 10) -> None:
        self.api_key = API_KEY
        self.call_cooldown = call_cooldown # seconds
        self.last_call_timestamp = -self.call_cooldown

    def complete(self, message_stream: List[Dict], model) -> str:
        if time.time() - self.last_call_timestamp < self.call_cooldown:
            return "Too many calls too fast."
        openai.api_key = self.api_key
        output = openai.ChatCompletion.create(
            model=model,
            messages=message_stream
        ).choices[0].message['content']
        self.last_call_timestamp = time.time()
        return output
