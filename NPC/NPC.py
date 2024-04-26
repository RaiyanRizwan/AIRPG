import random
from NPC.Memory import Memory
from NPC.Prompts import Prompts
from GPTEndpoint import GPTEndpoint
from Log import Log
from typing import List

class NPC:

    # TODO: implement function to summarize and enter dialogue into memory when end of conversation occurs

    """A generative NPC. Architectural ideas inspired from https://doi.org/10.1145/3586183.3606763."""

    def __init__(
            self, name: str, pronoun: str, age: int, 
            traits: List[str], initial_description: str, statuses: List[str],
            time, reflection_buffer_length: int, memory: Memory, LLM: GPTEndpoint, log: Log
    ) -> None:
        # characteristics
        self.name = name
        self.traits = traits
        self.statuses = statuses
        self.pronoun = pronoun
        self.age = age

        # external
        self.LLM = LLM
        self.log = log
        self.memory = memory
        self.prompt = Prompts(self)

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
        msg_stream = [{"role": "user", "content": self.prompt.core_characteristics(statements)}]
        core_nature = self.LLM.complete(msg_stream)
        
        # life progress
        statements = self.memory.query(f'{self.name}\'s recent life progress.', 3, time) # statements relevant to life progress
        msg_stream = [{"role": "user", "content": self.prompt.life_progress(statements)}]
        life_progress = self.LLM.complete(msg_stream)

        self.character_summary = self.prompt.character_summary(core_nature, life_progress)
        self.log.log(f'{self.name} generated a character summary: \n {self.character_summary}')

    def observe(self, observation: str, time) -> None:
        """Record observation."""
        self.memory.record(observation, time)
    
    def reflect(self, time) -> None:
        """Condense last [self.reflection_buffer_length] memories into a high-level reflection (also entered into the memory stream)."""
        recent_memories = self.memory.memories_text[-self.reflection_buffer_length:]
        msg_stream = [{'role':'system', 'content': self.prompt.WORLD_PREDICATE},
                      {'role':'user', 'content':self.prompt.salient_questions(recent_memories)}]
        questions = self.LLM.complete(msg_stream).split('\n')
        self.log.log(f'salient questions for {self.name}: {";".join(questions)}')
        for question in questions: 
            relevant_memories = self.memory.query(question, 5, time)
            insight = self.LLM.complete([{'role':'system', 'content': self.prompt.WORLD_PREDICATE + self.prompt.GENERAL_STYLE_PREDICATE},
                                          {'role':'user', 'content':self.prompt.insight(relevant_memories)}])
            self.memory.record(insight, time)
            self.log.log(f'{self.name} had the following reflection: {insight} in response to the question {question}.')

    def dialogue(self, status: str, dialogue_history: List[str], receiver_name: str, time) -> str:
        """Generate a reply to the receiver given the current dialogue history.
        dialogue_history: [name: speech, name: speech...]
        status: what the NPC is currently doing in the world"""
        relevant_memories_receiver = self.memory.query(f'Who is {receiver_name}?', 1, time)
        relevant_memories_dialogue = self.memory.query(dialogue_history[-1], 3, time) if len(dialogue_history) > 0 else []
        context = self.LLM.complete(message_stream=[{'role':'user', 'content':self.prompt.dialogue_context(receiver_name, relevant_memories_receiver, relevant_memories_dialogue)}])
        self.log.log(f'Dialogue prompt: {self.prompt.dialogue(status, context, dialogue_history, time)}')
        return self.LLM.complete(message_stream=[{'role':'system', 'content': self.prompt.WORLD_PREDICATE + self.prompt.DIALOGUE_STYLE_PREDICATE + self.prompt.DIALOGUE_STYLE_PREDICATE_EXAMPLE}, 
                                                 {'role':'user', 'content':self.prompt.dialogue(status, context, dialogue_history, time)}])

    def synthesize_dialogue(self, status: str, dialogue_history: List[str], time) -> None:
        """Summarize conversation and enter into memory."""
        summary = self.LLM.complete(message_stream=[{'role': 'system', 'content': self.prompt.WORLD_PREDICATE + self.prompt.GENERAL_STYLE_PREDICATE},
                                                    {'role': 'user', 'content': self.prompt.dialogue_summary(status, dialogue_history, time)}])
        for statement in summary.split('\n'): self.observe(statement, time)

    def random_state(self):
        '''
            Return a random state that this NPC could be in
        '''
        return random.choice(self.statuses)
    
    def __eq__(self, value: object) -> bool:
        if isinstance(value, NPC):
            return self.name == value.name
        return False
    
    def __hash__(self) -> int:
        return hash(self.name)
