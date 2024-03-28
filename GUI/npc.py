from random import choice

class BaseNPC():
    '''
        Abstract NPC class that all NPCs MUST extend for the GUI to work
        This is where the NPC system and the GUI connect.
    '''

    def __init__(self, name: str, sprite: str) -> None:
        self.name = name
        self.sprite = sprite # File path of image
        self.is_alive = True
    
    def respond_to(self, prompt: str) -> str:
        # Given a prompt by the player, what is this NPCs response
        return ''
    

    


class DummyNPC(BaseNPC):
    '''
        Extends BaseNPC with random text
    '''
    potential_responses = [
        "Hello there, traveler!",
        "What brings you to our town?",
        "Ah, what a beautiful day it is, don't you think?",
        "Have you heard the latest news? About the hidden grove?",
        "I could use some help with a small problem...",
        "Beware the woods at night; strange things happen there.",
        "Can you spare a moment?",
        "You look like you've come a long way.",
        "Greetings! What can I do for you?",
        "Watch your step around here; it can be quite dangerous.",
        "The weather's been odd lately, hasn't it?",
        "I've got something you might be interested in.",
        "Care to trade? I have some fine goods.",
        "Have you met the mayor yet?",
        "There's a legend about the old ruins just outside town...",
        "You seem like a seasoned adventurer.",
        "Do you have any stories to tell?",
        "If you're looking for work, I might have a task for you.",
        "The harvest festival is coming up soon.",
        "I wouldn't go near the old well if I were you.",
        "Ever seen a ghost? I swear this place is haunted. Especially near the hidden grove",
        "Keep an eye on your belongings; thieves are about.",
        "Ah, fresh faces in town. Welcome!",
        "If you need supplies, you've come to the right place.",
        "Safe travels, my friend.",
        "May fortune favor you.",
        "If you're heading into the forest, take this.",
        "You look like you could use a good meal.",
        "Care for a game of cards?",
        "Have you seen my cat? She's been missing since yesterday.",
        "The blacksmith makes the finest swords in the land.",
        "The old tower? It's been abandoned for years.",
        "We don't take kindly to troublemakers here.",
        "I heard there's treasure hidden beneath the hidden grove.",
        "The nights have been so cold lately.",
        "You wouldn't happen to know a good remedy for a cold, would you?",
        "A storm's coming. I can feel it in my bones.",
        "My garden's been thriving this season.",
        "There's a secret path through the mountains. It might get you to the hidden grove",
        "I'm looking for a rare herb; perhaps you've come across it?",
        "You're not from around here, are you?",
        "The old bridge is out; you'll have to find another way.",
        "I could tell you stories that would make your hair stand on end.",
        "Fancy a drink? The tavern's got the best ale.",
        "The library holds many ancient tomes and secrets.",
        "I once traveled far and wide, just like you.",
        "This land is full of mysteries waiting to be uncovered.",
        "Take care not to stray too far from the path. Or else you might find the hidden grove!",
        "We're expecting a caravan from the east any day now.",
        "You remind me of someone I used to know.",
        "The festival tonight will be one to remember!",
        "Be wary of the wolves; they've been bold of late.",
        "A good sword arm is always welcome here.",
        "There's a cave nearby that's yet to be explored.",
        "I've been crafting a new potion, but it's missing one final ingredient.",
        "Legends speak of a hero who will find the hidden grove.",
        "I wish I could see the ocean just once.",
        "If you're looking for adventure, you've found the right place.",
        "Our village is small, but we have big hearts.",
        "The stars have been strangely bright these past nights.",
        "My ancestors built this town centuries ago.",
        "I've got a riddle for you, if you're up for the challenge.",
        "You wouldn't believe what I found in the forest.",
        "This necklace has been in my family for generations.",
        "If you hear strange music at night, best stay indoors.",
        "I'm in need of a brave soul for a daring quest.",
        "The hidden grove is said to be cursed.",
        "I can teach you a thing or two about magic.",
        "The best fishing spots are kept secret around here.",
        "I've seen things in the dark that would turn your blood cold.",
        "A hearty meal is waiting for you at the inn.",
        "The art of potion-making is a delicate craft.",
        "There's a hidden grove where the fairies dance.",
        "Would you care to join us for the harvest?",
        "I'm searching for a song, the one that the wind sings.",
        "A true warrior knows when to fight and when to show mercy.",
    ]

    def respond_to(self, prompt: str) -> str:
        return choice(DummyNPC.potential_responses)