import pygame as pg
from pygame.surface import Surface
from typing import Tuple
import sys

# Constants


# Helper Classes
class NPC():
    # TODO: implement this

    def __init__(self) -> None:
        pass



class AIVN:
    DEBUG = False
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 576
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    class Rect(pg.Rect):
        def __init__(self, x: int, y: int, width: int, height: int) -> None:
            super().__init__(x, y, width, height)
            self.width = width
            self.height = height
            self.x = x
            self.y = y
        
        def get_pos(self, x_off=0, y_off=0):
            return (self.x + x_off, self.y + y_off)
        
        def get_dim(self, w_off=0, h_off=0):
            return (self.width + w_off, self.height + h_off)


    class BaseImage(Rect):
        def __init__(self, img_src: str, x: int, y: int, width: int, height: int, is_bkg=False) -> None:
            super().__init__(x, y, width, height)
            self.img_src = img_src
            self.image = pg.image.load(img_src)
            if not is_bkg:
                self.x, self.y = x - width // 2, y - height // 2

        def get_image(self) -> Surface:
            return pg.transform.scale(self.image, self.get_dim())


    class ImageBackground(BaseImage):
        def __init__(self, img_src: str) -> None:
            super().__init__(img_src, 0, 0, AIVN.SCREEN_WIDTH, AIVN.SCREEN_HEIGHT, True)


    class NPCLocation(Rect):
        image = pg.image.load('./assets/waypoint_icon.png')

        def __init__(self, name: str, NPC: NPC, x: int, y: int, width: int, height: int) -> None:
            # Generate a waypoint based on the POINT IT IS POINTING AT (NOT TOP LEFT)
            self.name = name
            super().__init__(x, y, width, height)
            self.x = x - width // 2
            self.y = y - height
            self.NPC = NPC
            self.has_player = False
            
        def get_image(self) -> Surface:
            return pg.transform.scale(AIVN.NPCLocation.image, (self.width, self.height))

        def get_pos(self, x_off=0, y_off=0):
                return (self.x + x_off, self.y + y_off)
            
        def get_dim(self, w_off=0, h_off=0):
            return (self.width + w_off, self.height + h_off)

        def __str__(self) -> str:
            return self.name + ": " + super().__str__()
        
        def __repr__(self) -> str:
            return self.name


    def __init__(self) -> None:
        self.cur_game_state = 1 # 0 for Title Screen, 1 for Map View, 2 for NPC View
        
        pg.init()
        self.screen = pg.display.set_mode((AIVN.SCREEN_WIDTH, AIVN.SCREEN_HEIGHT))
        
        # Game Loop Instance Vars
        self.npc_locs = {
            "castle": self.NPCLocation("castle", NPC(), 370, 214, 70, 70),
            "farm": self.NPCLocation("farm", NPC(), 830, 378, 70, 70), 
            "red_house": self.NPCLocation("red_house", NPC(), 853, 254, 70, 70),
            "blue_house": self.NPCLocation("blue_house", NPC(), 153, 432, 70, 70)
        }
        self.assets = {
            "map": self.ImageBackground('./assets/map.png'),
            "castle": self.ImageBackground('./assets/castle.png'),
            "farm": self.ImageBackground('./assets/farm.png'),
            "red_house": self.ImageBackground('./assets/red_house.png'),
            "blue_house": self.ImageBackground('./assets/blue_house.png'),
            "font": pg.font.Font(None, 32),
            "player_input": self.Rect(100, 450, 900, 90),
            "NPC_response": self.Rect(100, 350, 900, 90),
            "go_back_icon": self.BaseImage('./assets/go_back.png', 30, 30, 40, 40),
            "temp_NPC_sprite": self.BaseImage('./assets/temp_char_sprite.png', AIVN.SCREEN_WIDTH // 2, AIVN.SCREEN_HEIGHT * 1.3 // 2, 150, 400)
        }
        self.cur_player_text = ''
        self.cur_NPC_text = ''
        self.cur_NPC = None
        self.cur_NPC_loc = None
    

    def alpha_fill(self, color: Tuple[int, int, int, int], rect: Rect) -> None:
        alpha_surface = pg.Surface(rect.get_dim(), pg.SRCALPHA)
        alpha_surface.fill(color)
        self.screen.blit(alpha_surface, rect.get_pos())

    def highlight(self, img: Surface) -> Surface:
        img = img.copy()
        for x in range(img.get_width()):
            for y in range(img.get_height()):
                color = img.get_at((x, y))

                # Check if the pixel is black
                if color == (0, 0, 0, 255):  
                    # highlight yellow
                    img.set_at((x, y), (190, 100, 0, 255))
        return img

    def title_loop(self) -> bool:
        # TODO: Implement this
        return False 


    def setup_map_loop(self) -> None:
        self.cur_game_state = 1
        for loc in self.npc_locs.values():
            loc.has_player = loc.name == self.cur_NPC_loc
                

    def map_loop(self) -> bool:
        # Runs map loop and returns a boolean indicating if the game should still run or not
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # Check if the mouse click is within any clickable region
                for loc in self.npc_locs.values():
                    if loc.collidepoint(mouse_pos):
                        self.setup_NPC_loop(loc)

                if AIVN.DEBUG:
                        print("Clicked within region at", event.pos)

        # Draw the map and waypoints
        self.screen.blit(self.assets["map"].get_image(), self.assets["map"].get_pos())
        for loc in self.npc_locs.values():
            if loc.has_player:
                self.screen.blit(self.highlight(loc.get_image()), loc.get_pos())
            else:
                self.screen.blit(loc.get_image(), loc.get_pos())
        pg.display.flip()

        return True


    def setup_NPC_loop(self, selected_loc: NPCLocation) -> None:
        self.cur_NPC_loc = selected_loc.name
        self.cur_NPC = selected_loc.NPC
        self.cur_game_state = 2
        self.cur_player_text = ''
        self.cur_NPC_text = ''


    def NPC_loop(self) -> bool:
        # Runs NPC loop with interactions back and forth between the NPC
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            # Check for Kill or Go Back to Map actions
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.assets["go_back_icon"].collidepoint(mouse_pos):
                    self.setup_map_loop()

            
            # Deal with player input
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.cur_NPC_text = "You typed: " + self.cur_player_text  # Example response handling
                    self.cur_player_text = ''  # Clear input text
                elif event.key == pg.K_BACKSPACE:
                    self.cur_player_text  = self.cur_player_text[:-1]
                else:
                    self.cur_player_text += event.unicode
            
            if AIVN.DEBUG:
                print("Clicked within region at", event.pos)
        
        self.screen.blit(self.assets[self.cur_NPC_loc].get_image(), self.assets[self.cur_NPC_loc].get_pos())
        self.screen.blit(self.assets["temp_NPC_sprite"].get_image(), self.assets["temp_NPC_sprite"].get_pos())

        # Render Player Input
        self.alpha_fill((100,100,100,180), self.assets["player_input"])
        player_surface = self.assets["font"].render(self.cur_player_text, True, AIVN.BLACK)
        self.screen.blit(player_surface, self.assets["player_input"].get_pos(5, 5))
        pg.draw.rect(self.screen, AIVN.BLACK, self.assets["player_input"], 2)

        # Render NPC Response
        self.alpha_fill((100,100,100,180), self.assets["NPC_response"])
        NPC_surface = self.assets["font"].render(self.cur_NPC_text, True, AIVN.BLACK)
        self.screen.blit(NPC_surface, self.assets["NPC_response"].get_pos(5, 5))
        pg.draw.rect(self.screen, AIVN.BLACK, self.assets["NPC_response"], 2)

        # Render all other components
        self.screen.blit(self.assets["go_back_icon"].get_image(), self.assets["go_back_icon"].get_pos())
        
        pg.display.flip()
        return True

    

    def start_game_loop(self) -> None:
        running = True
        action_map = {0: self.title_loop, 1: self.map_loop, 2: self.NPC_loop}
        while running:
            running = action_map[self.cur_game_state]()
        # Quit Pygame
        pg.quit()




new_game = AIVN()
new_game.start_game_loop()

