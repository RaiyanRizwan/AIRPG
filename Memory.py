import re
import faiss
import numpy as np
from GPTEndpoint import GPTEndpoint

class Memory:
    
    IMPORTANCE_PROMPT = """On a scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is \
        extremely poignant (e.g., a break up, college acceptance, murder), rate the likely poignancy of the following memory."""
    
    def __init__(self, importance_threshold: float, embeddings_batch_size: int, embedding_length: int, gpt_endpoint: GPTEndpoint) -> None:
        """
            importance_threshold: memories with importance below this threshold will not be stored.
            embeddings_batch_size: number of memories in the record buffer (holds memories not yet processed into embeddings).
            embedding_length: dimensions parameter for embeddings.
        """
        # params
        self.importance_threshold = importance_threshold # between [0, 10]
        self.embeddings_batch_size = embeddings_batch_size
        self.embedding_dim = embedding_length
        self.GPT = gpt_endpoint
        
        # structures
        self.record_buffer = [] 
        self.memories_text = []
        self.memories_embeddings = []
        self.memories_timestamps = []
    
    def record(self, memory_text: str) -> None:
        if self.important(memory_text):
            self.record_buffer.append(memory_text)
            if len(self.record_buffer) == self.embeddings_batch_size:
                embeddings = self.GPT.embedding(self.record_buffer, dimensions=self.embedding_dim)
                # TODO: add to memory stream
    
    def important(self, memory_text: str) -> bool:
        msg_stream = [{'role':'system', 'content':self.IMPORTANCE_PROMPT}, 
                      {"role": "user", "content": f'Memory: {memory_text} \n Rating: <fill in>'}]
        response = self.GPT.complete(msg_stream, 'gpt-3.5-turbo-0125')
        match = re.search(r'\d+', response)
        importance = 10 # default value in case of exceptions
        try:
            if match:
                importance = int(match.group())
            else:
                # TODO: trigger save game state
                raise RuntimeError('Could not determine importance.')
        except ValueError as e:
            # TODO: trigger save game state
            print(f"Unexpected error while determining importance: {e}")
        return importance >= self.importance_threshold
    