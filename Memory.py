import re
import faiss
from GPTEndpoint import GPTEndpoint
from typing import List
from Log import Log

class Memory:
    
    IMPORTANCE_PROMPT = """On a scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is \
        extremely poignant (e.g., a break up, college acceptance, murder), rate the likely poignancy of the following memory."""
    
    def __init__(self, importance_threshold: float, 
                 embeddings_batch_size: int, 
                 embedding_length: int,
                 recency_weight: int,
                 relevance_weight: int,
                 gpt_endpoint: GPTEndpoint, 
                 log: Log) -> None:
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
        self.log = log
        
        # structures
        self.text_record_buffer = [] 
        self.timestamp_record_buffer = []
        self.memories_text = []
        self.memories_timestamps = []
        
        # faiss (mem query)
        self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
        self.recency_weight = recency_weight
        self.relevance_weight = relevance_weight
    
    def record(self, memory_text: str, timestamp) -> None:
        """Record a memory to the memory system (may not actually enter the stream until the record buffer is full)."""
        if self.important(memory_text):
            self.text_record_buffer.append(memory_text)
            self.timestamp_record_buffer.append(timestamp)
            if len(self.text_record_buffer) == self.embeddings_batch_size:
                # process embeddings in a batch
                embeddings = self.GPT.embedding(self.text_record_buffer, dimensions=self.embedding_dim)
                # faiss process
                self.faiss_index.add(embeddings)
                # add to memory stream
                self.memories_text.extend(self.text_record_buffer)
                self.memories_timestamps.extend(self.timestamp_record_buffer)
                # empty buffers
                self.text_record_buffer = []
                self.timestamp_record_buffer = []
                
    def query(self, query_text: str, k: int, current_time) -> List[str]:
        """Return the k memories most relevant to the given query."""
        query_embedding = self.GPT.embedding([query_text], dimensions=self.embedding_dim)[0]
        distances, nearest_neighbor_indices = self.faiss_index.search(query_embedding.reshape(1, -1), k) # sorted by increasing dist from query
        
        scores = []
        for idx, faiss_idx in enumerate(nearest_neighbor_indices[0]):
            time_delta = current_time - self.memories_timestamps[faiss_idx]
            relevance = 1 / (distances[0][idx] + 0.0001)  # add small value to prevent division by zero
            score = self.recency_weight * (1 / time_delta) + self.relevance_weight * relevance
            scores.append((score, faiss_idx))
        
        sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)
        return [self.memories_text[idx] for _, idx in sorted_scores[:k]]

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
                self.log.log(f'Importance regex failed for memory {memory_text}.')
                raise RuntimeError('Could not determine importance.')
        except ValueError as e:
            self.log.log(f'Error {e} while determining importance of memory {memory_text}.')
            print(f"Unexpected error while determining importance: {e}")
        return importance >= self.importance_threshold
    