class Prompts:

    def __init__(self, NPC) -> None:

        self.NPC = NPC

        # Establish the nature of the world the characters are in.
        self.WORLD_PREDICATE = 'Assume the medeival, fantastical world is reality. Never break the fourth wall. Magic is real.'

        # Establish response style (grammar, length, etc.) for reflections and character synthesis.
        self.GENERAL_STYLE_PREDICATE = 'Speak in absolutes. Be concise and substantive.'

        # Establish response style (grammar, length, etc.) for dialogue.
        self.DIALOGUE_STYLE_PREDICATE = 'Be concise and substantive. Always respond in the format <character> : <speech>.'

        # Few shot prompting examples.
        self.DIALOGUE_STYLE_PREDICATE_EXAMPLE = "Some examples: " + " ".join([
                                                                    'Alaric: For honor and glory!',
                                                                    "Mira: Magic is not just power; it's wisdom.",
                                                                    'Thorne: Shadows are my best allies.',
                                                                    'Elara: My aim is true, as is my heart.',
                                                                    'Drogan: Roarrr! Treasure? Mine!'
                                                                ])
    
    def core_characteristics(self, statements):
        """statements: statements relevant to core characteristics of NPC"""
        return self.GENERAL_STYLE_PREDICATE + f'How would you describe {self.NPC.name}\'s core characteristics given the following statements?' + '\n'.join(statements)

    def life_progress(self, statements):
        """statements: statements relevant to how NPC is feeling about their life progress"""
        return self.GENERAL_STYLE_PREDICATE + f'How would you describe {self.NPC.name}\'s feelings about {self.NPC.pronoun} current progress in life given the following statements?' + '\n'.join(statements)
    
    def character_summary(self, *args):
        """return character summary"""
        return f'Name: {self.NPC.name} (age: {self.NPC.age}) \n Tone/Personality (ENSURE YOU TALK IN THIS MANNER, THIS IS OF UTMOST IMPORTANCE): {", ".join(self.NPC.traits)} \n {args}'
    
    def salient_questions(self, recent_memories):
        """generate salient questions prompt (for reflections)"""
        return f'Given only the information below, what are 3 most salient highlevel questions we can answer about the subjects in the statements? Separate with newlines. \n' +  "\n".join(recent_memories)

    def insight(self, relevant_memories):
        """generate insight from memories (out: reflection)"""
        return '\n'.join(relevant_memories) + '\n' + 'What one-sentence high-level insight can you infer from the above statements?'
    
    def dialogue_context(self, receiver_name, relevant_memories_receiver, relevant_memories_dialogue):
        """summarize NPC's memories that are relevant to what's being spoken about"""
        return f'{self.NPC.name} is speaking to {receiver_name}. Briefly summarize the context given what {self.NPC.name} remembers: \n' + '\n'.join(relevant_memories_receiver + relevant_memories_dialogue)
    
    def dialogue(self, status, context, dialogue_history, time):
        """dialogue prompt"""
        return self.NPC.character_summary + '\n' + \
                str(time) + '\n' + \
                status + '\n' + \
                f'You ONLY know whatever is in the following context. Summary of relevant context from {self.NPC.name}\'s memory: ' + \
                context + '\n' \
                'Here is the dialogue history:' + '\n' + \
                '\n'.join(dialogue_history) + '\n' + \
                f'You are {self.NPC.name}. How would you respond?'
    
    def dialogue_summary(self, status, dialogue_history, time):
        """dialogue summary prompt"""
        return self.NPC.character_summary + '\n' + \
                str(time) + '\n' + \
                status + '\n' + \
                'Dialogue history:' + '\n' + \
                '\n'.join(dialogue_history) + '\n' + \
                f'Succinctly summarize the conversation into two or three salient, new-line separated statements based primarily on the given dialogue history..'
    