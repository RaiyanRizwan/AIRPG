from NPC.Memory import Memory
from GPTEndpoint import GPTEndpoint

class NPC:

    def __init__(self, name: str, memory: Memory, LLM: GPTEndpoint, initial_description: str) -> None:
        self.name = name
        self.memory = memory
        self.LLM = LLM
        self.character_summary = initial_description

    def synthesize_summary(self) -> None:
        """Dynamically generate concise agent summary."""
        statements = self.memory.query(f'{self.name}\'s core characteristics.') # statements relevant to core characteristics
        msg_stream = [{'role':'system', 'content':f'How would you describe {self.name}\'s core characteristics given the following statements?'}, 
                      {"role": "user", "content": '\n'.join(['-' + s for s in statements])}]
        self.character_summary = self.LLM.complete(msg_stream)
