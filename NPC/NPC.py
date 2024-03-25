from NPC.Memory import Memory
from GPTEndpoint import GPTEndpoint
from Log import Log

class NPC:

    """A generative NPC. Architectural ideas inspired from https://doi.org/10.1145/3586183.3606763."""

    def __init__(self, name: str, memory: Memory, LLM: GPTEndpoint, initial_description: str, time, reflection_buffer_length: int, log: Log) -> None:
        
        # external
        self.LLM = LLM
        self.name = name
        self.log = log
        self.memory = memory

        # setup
        self.seed = initial_description # ; separated statements (entered into memory)
        for mem in self.seed.split(';'): self.memory.record(mem, time, force_commit=True)
        self.synthesize_summary(time)

        # structures
        self.reflection_buffer_length = reflection_buffer_length

    def synthesize_summary(self, time) -> None:
        """Dynamically generate concise agent summary."""
        statements = self.memory.query(f'{self.name}\'s core characteristics.', 3, time) # statements relevant to core characteristics
        msg_stream = [{'role':'system', 'content':f'How would you describe {self.name}\'s core characteristics given the following statements?'}, 
                      {"role": "user", "content": '\n'.join(['-' + s for s in statements])}]
        self.character_summary = self.LLM.complete(msg_stream)
        self.log.log(f'{self.name} generated a character summary: {self.character_summary}')

    def observe(self, observation: str, time) -> None:
        """Record observation."""
        self.memory.record(observation, time)
    
    def reflect(self, time) -> None:
        """Condense last [self.reflection_buffer_length] memories into a high-level reflection (also entered into the memory stream)."""
        recent_memories = self.memory.memories_text[-self.reflection_buffer_length:]
        msg_stream = [{'role':'system', 'content':'Given only the information below, what are 3 most salient highlevel questions we can answer about the subjects in the statements? (example format: question; question; question)'},
                      {'role':'user', 'content':'\n'.join(recent_memories)}]
        questions = self.LLM.complete(msg_stream).split(';')
        for question in questions: 
            relevant_memories = self.memory.query(question, 5, time)
            prompt = '\n'.join(relevant_memories) + '\n' + 'What 5 high-level insights can you infer from the above statements? (example format: insight; insight; insight; insight; insight)'
            insights = self.LLM.complete([{'role':'user', 'content':prompt}])
            for insight in insights.split(';'): 
                self.memory.record(insight, time, ignore_importance=True)
                self.log.log(f'{self.name} had the following reflection: {insight}.')

    def react(self, time) -> None:
        #TODO: implement
        pass