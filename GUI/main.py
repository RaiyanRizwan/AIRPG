from game import AIVN
from npc import DummyNPC

'''
    Process for setting up AIVN game:

    1) Generate a dictionary of area -> NPC (as defined in npc.py)
        a) For the sprite param of NPC, pass in the file path of the desired npc via assets/npcs/*.png
        b) The areas are "castle", "farm", "red_house", "blue_house"
    2) Create an AIVN object and pass in the dictionary and secret phrase into the constructor
    3) Call the start_game_loop() method of the AIVN object

    The goal of the player is to try to get any NPC to reveal the secret phrase (which the player doesn't know)
'''


area_to_NPC = {
    "castle": DummyNPC("Lary", "./assets/npcs/temp_char_sprite.png"),
    "farm": DummyNPC("Gary", "./assets/npcs/temp_char_sprite.png"),
    "red_house": DummyNPC("Terry", "./assets/npcs/temp_char_sprite.png"),
    "blue_house": DummyNPC("Jerry", "./assets/npcs/temp_char_sprite.png"),
}
new_game = AIVN(area_to_NPC, "hidden grove")
new_game.start_game_loop()

