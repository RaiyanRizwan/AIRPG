import re
import faiss
from NPC.utils import scale_to_range, normalize_vectors
from GPTEndpoint import GPTEndpoint
from typing import List
from Log import Log

#TODO: investigate why using batch size > 1 causes odd results

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
        self.LLM = gpt_endpoint
        self.log = log
        
        # structures
        self.text_record_buffer = [] 
        self.timestamp_record_buffer = []
        self.memories_text = []
        self.memories_timestamps = []
        
        # faiss (mem query)
        self.faiss_index = faiss.IndexFlatL2(self.embedding_dim) # normalize all incoming vectors = FAISS w/ cosine similarity 
        self.recency_weight = recency_weight
        self.relevance_weight = relevance_weight
    
    def record(self, memory_text: str, timestamp, force_commit: bool = False) -> None:
        """Record a memory to the memory system (may not actually enter the stream until the record buffer is full)."""
        if self.important(memory_text):
            self.text_record_buffer.append(memory_text)
            self.timestamp_record_buffer.append(timestamp)
            if force_commit or len(self.text_record_buffer) == self.embeddings_batch_size:
                # process embeddings in a batch
                embeddings = self.LLM.embedding(self.text_record_buffer, dimensions=self.embedding_dim)
                # faiss process
                self.faiss_index.add(normalize_vectors(embeddings))
                # add to memory stream
                self.memories_text.extend(self.text_record_buffer)
                self.memories_timestamps.extend(self.timestamp_record_buffer)
                # empty buffers
                self.text_record_buffer = []
                self.timestamp_record_buffer = []
                
    def query(self, query_text: str, k: int, current_time) -> List[str]:
        """Return the k memories most pertinent to the given query based on a weighted sum of cosine similarity and recency."""
        query_embedding = self.LLM.embedding([query_text], dimensions=self.embedding_dim)[0]
        distances, nearest_neighbor_indices = self.faiss_index.search(normalize_vectors([query_embedding])[0].reshape(1, -1), k)

        time_deltas = [current_time - self.memories_timestamps[faiss_idx] for faiss_idx in nearest_neighbor_indices[0]]
        relevances = [1 / (dist + 0.0001) for dist in distances[0]]  # to prevent division by zero
        scaled_time_deltas = scale_to_range(time_deltas, MAX=1)
        scaled_relevances = scale_to_range(relevances, MAX=1)

        scores = []
        for time_delta, relevance, idx in zip(scaled_time_deltas, scaled_relevances, nearest_neighbor_indices[0]):
            score = self.recency_weight * time_delta + self.relevance_weight * relevance
            scores.append((score, idx))
        
        sorted_scores = sorted(scores, key=lambda x: x[0], reverse=True)[:k]
        return [self.memories_text[idx] for _, idx in sorted_scores]

    def important(self, memory_text: str) -> bool:
        """Ask the LLM for an importance score regarding the memory."""
        msg_stream = [{'role':'system', 'content':self.IMPORTANCE_PROMPT}, 
                      {"role": "user", "content": f'Memory: {memory_text} \n Rating: <fill in>'}]
        response = self.LLM.complete(msg_stream)
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
        self.log.log(f'Memory: {memory_text}, Importance: {importance}.')
        return importance >= self.importance_threshold
    