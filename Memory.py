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
        self.text_record_buffer = [] 
        self.timestamp_record_buffer = []
        self.memories_text = []
        self.memories_embeddings = []
        self.memories_timestamps = []
    
    def record(self, memory_text: str, timestamp) -> None:
        """Record a memory to the memory system (may not actually enter the stream until the record buffer is full)."""
        if self.important(memory_text):
            self.text_record_buffer.append(memory_text)
            self.timestamp_record_buffer.append(timestamp)
            if len(self.text_record_buffer) == self.embeddings_batch_size:
                # process embeddings in a batch
                embeddings = self.GPT.embedding(self.text_record_buffer, dimensions=self.embedding_dim)
                # add to memory stream
                self.memories_text.extend(self.text_record_buffer)
                self.memories_embeddings.extend(embeddings)
                self.memories_timestamps.extend(self.timestamp_record_buffer)
                # empty buffers
                self.text_record_buffer = []
                self.timestamp_record_buffer = []
                
    def query(self, query_text: str) -> str:
        """Return the memories most relevant to the given query."""
        pass
    
    def important(self, memory_text: str) -> bool:
        """Ask the LLM for an importance score regarding the memory."""
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
    