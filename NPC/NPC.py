from NPC.Memory import Memory
from GPTEndpoint import GPTEndpoint

class NPC:

    """A generative NPC. Architectural ideas derived from https://doi.org/10.1145/3586183.3606763."""

    def __init__(self, name: str, memory: Memory, LLM: GPTEndpoint, initial_description: str, time) -> None:
        self.LLM = LLM
        self.name = name
        self.memory = memory
        self.seed = initial_description # ; separated statements (entered into memory)
        for mem in self.seed.split(';'): self.memory.record(mem, time, force_commit=True)
        self.synthesize_summary()

    def synthesize_summary(self) -> None:
        """Dynamically generate concise agent summary."""
        statements = self.memory.query(f'{self.name}\'s core characteristics.') # statements relevant to core characteristics
        msg_stream = [{'role':'system', 'content':f'How would you describe {self.name}\'s core characteristics given the following statements?'}, 
                      {"role": "user", "content": '\n'.join(['-' + s for s in statements])}]
        self.character_summary = self.LLM.complete(msg_stream)

    def observe(self, observation: str, time) -> None:
        """Record observation."""
        self.memory.record(observation, time)
    
    def reflect(self, time) -> None:
        #TODO: implement
        pass

    def react(self, time) -> None:
        #TODO: implement
        pass