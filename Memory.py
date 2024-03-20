import numpy as np
import faiss
from GPTEndpoint import GPTEndpoint

class Memory:
    
    IMPORTANCE_PROMPT = """On a scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is \ 
    extremely poignant (e.g., a break up, college acceptance, murder), rate the likely poignancy of the following memory."""
    
    def __init__(self, importance_threshold: float, embeddings_batch_size: int, embedding_length: int, gpt_endpoint: GPTEndpoint) -> None:
        """
            importance_threshold: memories with importance below this threshold will not be stored.
            embeddings_batch_size: number of memories in the record buffer (stores memories not yet embedding-batch processed).
            embedding_length: dimensions parameter for embeddings.
        """
        self.record_buffer = [] 
        self.embeddings_batch_size = embeddings_batch_size
        self.GPT = gpt_endpoint
    
    def record(self, memory_text: str) -> None:
        if self.important(memory_text):
            self.record_buffer.append(memory_text)
            if len(self.record_buffer) == self.embeddings_batch_size:
                pass
                # TODO: generate embeddings and add to memory stream
    
    def important(self, memory_text: str) -> bool:
        msg_stream = [{'role':'system', 'content':self.IMPORTANCE_PROMPT}, 
                      {"role": "user", "content": f'Memory: {memory_text} \n Rating: <fill in>'}]
        importance = self.GPT.complete(msg_stream, 'gpt-3.5-turbo-0125')
        # TODO: test and return true if importance > self.threshold
        return True