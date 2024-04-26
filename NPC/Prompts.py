

class Prompts:

    def __init__(self, NPC) -> None:

        self.NPC = NPC

        # Establish the nature of the world the characters are in.
        self.WORLD_PREDICATE = 'This is the world of Aleria, a fantasy world where a large castle Morne is in the center of the Town. Surrounding the Town is the vast Outskirts, filled with dangerous beasts, and the Ruined Castle Grimlock, home of the evil baron. There is also much treasure to be gained from exploring the Outskirts, but it is risky. Assume the world of Aleria AT ALL TIMES. NEVER BREAK THE FOURTH WALL!'

        # Establish response style (grammar, length, etc.) for reflections and character synthesis.
        self.GENERAL_STYLE_PREDICATE = 'Speak in absolutes. Be concise.'

        # Establish response style (grammar, length, etc.) for dialogue.
        self.DIALOGUE_STYLE_PREDICATE = 'Be concise, and act as a realistic character within the game. Always respond in the format <character> : <speech>.'

        # Few shot prompting examples.
        self.DIALOGUE_STYLE_PREDICATE_EXAMPLE = "Some examples: " + " ".join([
                                                                    'Alaric: Thank you for coming to meet me. It\'s been too long...',
                                                                    "Mira: No way...heh, I can't believe he fell for that",
                                                                    'Thorne: I stay in the shadows, biding my time for when I can strike! Or you know, eat lunch.',
                                                                    'Elara: Oh my gosh! That is like, so hard to believe.',
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
    
    @staticmethod
    def player_emotion_level(player, NPC, relevant_memories):
        return '\n'.join(relevant_memories) + '\n' + f'Based on the dialogue between {player} and {NPC}, generate a number from -10 to 10 based on how much {player} seems to likes or dislikes {NPC}. -10 means an absolute hatred, 0 means completely neutral, and 10 means absolute love. YOU CAN ONLY RETURN A NUMBER FROM -10 to 10! '
    
    def emotion_level(self, reciever_name, relevant_memories):
        '''generate emotion level from -10 to 10'''
        return '\n'.join(relevant_memories) + '\n' + f'Based on these memories about {reciever_name} from {self.NPC.name}, generate a number from -10 to 10 based on how much {self.NPC.name} likes or dislikes {reciever_name}. -10 means an absolute hatred, 0 means completely neutral, and 10 means absolute love. YOU CAN ONLY RETURN A NUMBER FROM -10 to 10! '
    
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