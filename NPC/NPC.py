from NPC.Memory import Memory
from GPTEndpoint import GPTEndpoint
from Log import Log
from typing import List

class NPC:

    """A generative NPC. Architectural ideas inspired from https://doi.org/10.1145/3586183.3606763."""

    WORLD_PREDICATE = 'Assume the medeival, fantastical world is reality. Never break the fourth wall. Magic is real.'
    STYLE_PREDICATE = 'Speak in absolutes. Be concise and substantive.'

    def __init__(self, name: str, pronoun: str, age: int, traits: List[str], memory: Memory, LLM: GPTEndpoint, initial_description: str, time, reflection_buffer_length: int, log: Log) -> None:
        
        # characteristics
        self.name = name
        self.traits = traits
        self.pronoun = pronoun
        self.age = age

        # external
        self.LLM = LLM
        self.log = log
        self.memory = memory

        # setup
        self.seed = initial_description # ; separated statements (entered into memory)
        for mem in self.seed.split(';'): self.memory.record(mem, time, force_commit=True, memory_importance=10)
        self.synthesize_summary(time)

        # structures
        self.reflection_buffer_length = reflection_buffer_length

    def synthesize_summary(self, time) -> None:
        """Dynamically generate concise agent summary."""

        # core nature
        statements = self.memory.query(f'{self.name}\'s core characteristics.', 3, time) # statements relevant to core characteristics
        msg_stream = [{"role": "user", "content": self.STYLE_PREDICATE + f'How would you describe {self.name}\'s core characteristics given the following statements?' + '\n'.join(statements)}]
        core_nature = self.LLM.complete(msg_stream)
        
        # life progress
        statements = self.memory.query(f'{self.name}\'s recent life progress.', 3, time) # statements relevant to life progress
        msg_stream = [{"role": "user", "content": self.STYLE_PREDICATE + f'How would you describe {self.name}\'s feelings about {self.pronoun} current progress in life given the following statements?' + '\n'.join(statements)}]
        life_progress = self.LLM.complete(msg_stream)

        self.character_summary = f'Name: {self.name} (age: {self.age}) \n Innate traits: {", ".join(self.traits)} \n {core_nature} {life_progress}'
        self.log.log(f'{self.name} generated a character summary: \n {self.character_summary}')

    def observe(self, observation: str, time) -> None:
        """Record observation."""
        self.memory.record(observation, time)
    
    def reflect(self, time) -> None:
        """Condense last [self.reflection_buffer_length] memories into a high-level reflection (also entered into the memory stream)."""
        recent_memories = self.memory.memories_text[-self.reflection_buffer_length:]
        msg_stream = [{'role':'system', 'content': self.WORLD_PREDICATE},
                      {'role':'user', 'content':'Given only the information below, what are 3 most salient highlevel questions we can answer about the subjects in the statements? (example format: question \n question)'},
                      {'role':'user', 'content':'\n'.join(recent_memories)}]
        questions = self.LLM.complete(msg_stream).split('\n')
        self.log.log(f'salient questions for {self.name}: {";".join(questions)}')
        for question in questions: 
            relevant_memories = self.memory.query(question, 5, time)
            prompt = '\n'.join(relevant_memories) + '\n' + 'What one-sentence high-level insight can you infer from the above statements?'
            insight = self.LLM.complete([{'role':'system', 'content': self.WORLD_PREDICATE + self.STYLE_PREDICATE},
                                          {'role':'user', 'content':prompt}])
            self.memory.record(insight, time)
            self.log.log(f'{self.name} had the following reflection: {insight} in response to the question {question}.')

    def react(self, time) -> None:
        #TODO: implement
        pass
