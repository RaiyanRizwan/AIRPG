import pygame as pg
from pygame.surface import Surface
from typing import Tuple, Dict
from collections import deque
from npc import BaseNPC as NPC


class AIVN:
    DEBUG = False
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 576
    TEXTBOX_BORDER_RADIUS = 12
    BUTTON_BORDER_RADIUS = 16
    FRAME_RATE = 1
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLOOD = (180, 12, 24)
    TRACK_LIST = {
        "title": "assets/audio/title_screen.mp3",
        "main": "assets/audio/test.mp3",
        "win": "assets/audio/victory.mp3"
    }

    '''
        ALL HELPER CLASSES FOR AIVN
    '''

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
    






    class AnimationManager():

        class AnimationTask():

            def __init__(self, screen: Surface, game_state: int, speed: float) -> None:
                self.game_state = game_state
                self.speed = speed
                self.screen = screen
                self.is_complete = False
            
            def tick(self) -> None:
                pass


        class FadeIn(AnimationTask):

            def __init__(self, screen: Surface, game_state: int, speed: float) -> None:
                super().__init__(screen, game_state, speed)
                self.fade_surface = pg.Surface((AIVN.SCREEN_WIDTH, AIVN.SCREEN_HEIGHT))
                self.fade_surface.fill(AIVN.BLACK)
                self.cur_alpha = 255

            def tick(self) -> None:
                self.cur_alpha -= self.speed
                if self.cur_alpha <= 0:
                    self.is_complete = True
                    self.cur_alpha = 0
                self.fade_surface.set_alpha(self.cur_alpha)
                self.screen.blit(self.fade_surface, self.fade_surface.get_rect())
        

        class FadeOut(AnimationTask):

            def __init__(self, screen: Surface, game_state: int, speed: float) -> None:
                super().__init__(screen, game_state, speed)
                self.fade_surface = pg.Surface((AIVN.SCREEN_WIDTH, AIVN.SCREEN_HEIGHT))
                self.fade_surface.fill(AIVN.BLACK)
                self.cur_alpha = 0

            def tick(self) -> None:
                self.cur_alpha += self.speed
                if self.cur_alpha >= 255:
                    self.is_complete = True
                    self.cur_alpha = 255
                self.fade_surface.set_alpha(self.cur_alpha)
                self.screen.blit(self.fade_surface, self.fade_surface.get_rect())
        

        class KillFlash(AnimationTask):

            def __init__(self, screen: Surface, game_state: int, speed: float) -> None:
                super().__init__(screen, game_state, speed)
                self.fade_surface = pg.Surface((AIVN.SCREEN_WIDTH, AIVN.SCREEN_HEIGHT))
                self.fade_surface.fill(AIVN.BLOOD)
                self.cur_alpha = 0
                self.hit_limit = False

            def tick(self) -> None:
                if not self.hit_limit:
                    self.cur_alpha += self.speed
                    if self.cur_alpha >= 255:
                        self.hit_limit = True
                        self.cur_alpha = 255
                else:
                    self.cur_alpha -= self.speed
                    if self.cur_alpha >= 0:
                        self.is_complete = True
                        self.cur_alpha = 0
                
                self.fade_surface.set_alpha(self.cur_alpha)
                self.screen.blit(self.fade_surface, self.fade_surface.get_rect())

        class Wait(AnimationTask):

            def __init__(self, screen: Surface, game_state: int, speed: float) -> None:
                super().__init__(screen, game_state, speed)
                self.timer = 0
                

            def tick(self) -> None:
                self.timer += self.speed
                if self.timer >= 300:
                    self.is_complete = True




        def __init__(self, screen:Surface) -> None:
            self.screen = screen
            self.current_tasks = deque()
            self.finished_tasks = deque()
            
            pairs = [
                ("fadein", self.FadeIn), 
                ("fadeout", self.FadeOut), 
                ("killflash", self.KillFlash), 
                ("wait", self.Wait)
            ]
            self.mapping = {}
            for p in pairs:
                self.mapping[p[0]] = p[1]
                self.mapping[p[1]] = p[0]
        

        def add_animation(self, type: str, game_state: str, speed=3) -> None:
            '''
                Potential Animations:
                "fadein" and "fadeout" currently
            '''
            try:
                self.current_tasks.append(self.mapping[type](self.screen, game_state, speed))
            except:
                raise Exception("Incorrect Animation Type")

        def tick(self) -> None:
            if len(self.current_tasks) == 0:
                return
            self.current_tasks[0].tick()
            if self.current_tasks[0].is_complete:
                self.finished_tasks.append(self.current_tasks.popleft())

        def has_any_task_finished(self) -> bool:
            return len(self.finished_tasks) > 0
        
        def get_finished_task(self) -> Tuple[str, int]:
            assert self.has_any_task_finished()

            task = self.finished_tasks.popleft()
            try:
                return (self.mapping[type(task)], task.game_state)
            except:
                raise Exception("Incorrect Animation Type")

        




    '''
        Helper Methods
    '''
    

    def alpha_fill(self, color: Tuple[int, int, int, int], rect: Rect, border_radius=0) -> None:
        alpha_surface = pg.Surface(rect.get_dim(), pg.SRCALPHA)
        pg.draw.rect(alpha_surface, color, alpha_surface.get_rect(), border_radius=border_radius)
        self.screen.blit(alpha_surface, rect.get_pos())


    def highlight(self, img: Surface, highlight_color=(33, 190, 44, 255)) -> Surface:
        img = img.copy()
        for x in range(img.get_width()):
            for y in range(img.get_height()):
                color = img.get_at((x, y))

                # Check if the pixel is black
                if color == (0, 0, 0, 255):  
                    # highlight yellow (or other inputted color)
                    img.set_at((x, y), highlight_color)
        return img

    def kill_NPC(self, npc: NPC):
        npc.is_alive = False
        self.animation_queue.add_animation("killflash", -1)

    def check_secret_word(self, response: str):
        # TODO: Implement Cosine Similarity detection. For now we use a simple check
        if self.secret_word in response:
            self.animation_queue.add_animation("wait", 2, speed=1)




    '''
        Start of AIVN Class
    '''




    def __init__(self, area_to_NPC: Dict[str, NPC], secret_word: str) -> None:
        self.cur_game_state = 0 # 0 for Title Screen, 1 for Map View, 2 for NPC View
        self.secret_word = secret_word

        
        pg.init()
        self.screen = pg.display.set_mode((AIVN.SCREEN_WIDTH, AIVN.SCREEN_HEIGHT))
        self.animation_queue = self.AnimationManager(self.screen)
        
        pg.mixer.init()
        self.cur_playing = "-1"

        
        # Game Loop Instance Vars
        self.npc_locs = {
            "castle": self.NPCLocation("castle", area_to_NPC["castle"], 370, 214, 70, 70),
            "farm": self.NPCLocation("farm", area_to_NPC["farm"], 830, 378, 70, 70), 
            "red_house": self.NPCLocation("red_house", area_to_NPC["red_house"], 853, 254, 70, 70),
            "blue_house": self.NPCLocation("blue_house", area_to_NPC["blue_house"], 153, 432, 70, 70)
        }
        self.assets = {
            "title_font": pg.font.Font(None, 90),
            "font": pg.font.Font(None, 32),

            "title_screen": self.ImageBackground('./assets/title_screen.png'),
            "start_button": self.Rect(AIVN.SCREEN_WIDTH // 2 - 125, 350, 250, 50),
            "title_text": self.Rect(AIVN.SCREEN_WIDTH // 2, 200, 200, 200),

            "map": self.ImageBackground('./assets/map.png'),
            "castle": self.ImageBackground('./assets/castle.png'),
            "farm": self.ImageBackground('./assets/farm.png'),
            "red_house": self.ImageBackground('./assets/red_house.png'),
            "blue_house": self.ImageBackground('./assets/blue_house.png'),

            "player_input": self.Rect(100, 430, 900, 90),
            "NPC_response": self.Rect(100, 330, 900, 90),
            "kill_button": self.Rect(100, 525, 125, 40),
            "go_back_icon": self.BaseImage('./assets/go_back.png', 30, 30, 40, 40),
            "temp_NPC_sprite": self.BaseImage('./assets/npcs/temp_char_sprite.png', AIVN.SCREEN_WIDTH // 2, AIVN.SCREEN_HEIGHT * 1.3 // 2, 150, 400),

            "secret_phrase_text": self.Rect(AIVN.SCREEN_WIDTH // 2, 320, 150, 150)

        }
        self.cur_player_text = ''
        self.cur_NPC_text = ''
        self.cur_NPC = None
        self.cur_NPC_loc = None




    def title_loop(self) -> bool:
        button = self.assets["start_button"]

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            if event.type == pg.MOUSEBUTTONDOWN:
                if button.collidepoint(event.pos):
                    self.setup_map_loop(0)

                if AIVN.DEBUG:
                    print("Clicked within region at", event.pos)

        # Draw the background image
        self.screen.blit(self.assets["title_screen"].get_image(), self.assets["title_screen"].get_pos())
        self.alpha_fill((100,100,100,130), self.assets["title_screen"])

        # Render the title text
        title_text = self.assets["title_font"].render('AI Visual Novel', True, AIVN.WHITE)
        self.screen.blit(title_text, self.assets["title_text"].get_pos(-title_text.get_width() // 2, 0)) 

        # Draw the "Get Started" button
        self.alpha_fill(AIVN.BLACK, button, border_radius=AIVN.BUTTON_BORDER_RADIUS)
        button_text = self.assets["font"].render('Get Started', True, AIVN.WHITE)
        self.screen.blit(button_text, button.get_pos(
                            (button.width - button_text.get_width()) // 2, 
                            (button.height - button_text.get_height()) // 2
                        )
        )

        return True





    def setup_map_loop(self, prev_state:int) -> None:
        for loc in self.npc_locs.values():
            loc.has_player = loc.name == self.cur_NPC_loc
        self.animation_queue.add_animation("fadeout", prev_state)
                

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
                        self.setup_NPC_loop(loc, 1)

                if AIVN.DEBUG:
                        print("Clicked within region at", event.pos)

        # Draw the map and waypoints
        self.screen.blit(self.assets["map"].get_image(), self.assets["map"].get_pos())
        for loc in self.npc_locs.values():
            if loc.has_player:
                self.screen.blit(self.highlight(loc.get_image()), loc.get_pos())
            elif not loc.NPC.is_alive:
                self.screen.blit(self.highlight(loc.get_image(), highlight_color=AIVN.BLOOD), loc.get_pos())
            else:
                self.screen.blit(loc.get_image(), loc.get_pos())

        return True




    def setup_NPC_loop(self, selected_loc: NPCLocation, prev_state: int) -> None:
        self.cur_NPC_loc = selected_loc.name
        self.cur_NPC = selected_loc.NPC
        self.cur_player_text = ''
        self.cur_NPC_text = ''
        self.animation_queue.add_animation("fadeout", prev_state)


    def NPC_loop(self) -> bool:
        # Runs NPC loop with interactions back and forth between the NPC

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            # Check for Kill or Go Back to Map actions
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.assets["go_back_icon"].collidepoint(mouse_pos):
                    self.setup_map_loop(2)
                if self.cur_NPC.is_alive and self.assets["kill_button"].collidepoint(mouse_pos):
                    self.kill_NPC(self.cur_NPC)
                if AIVN.DEBUG:
                    print("Clicked within region at", event.pos)

            # Deal with player input
            elif self.cur_NPC.is_alive and event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    # NPC Responds based on NPC type. Check if the NPC revealed the secret
                    self.cur_NPC_text = self.cur_NPC.respond_to(self.cur_player_text)
                    self.check_secret_word(self.cur_NPC_text)
                    self.cur_player_text = ''  # Clear input text
                elif event.key == pg.K_BACKSPACE:
                    self.cur_player_text  = self.cur_player_text[:-1]
                else:
                    self.cur_player_text += event.unicode



        # Render Death Screen
        if not self.cur_NPC.is_alive:
            self.screen.blit(self.assets[self.cur_NPC_loc].get_image(), self.assets[self.cur_NPC_loc].get_pos())
            self.current_player_text = "Their blood is on your hands..."
            
            self.alpha_fill((100,100,100,180), self.assets["player_input"], border_radius=AIVN.TEXTBOX_BORDER_RADIUS)
            NPC_surface = self.assets["font"].render(self.current_player_text, True, AIVN.BLOOD)
            self.screen.blit(NPC_surface, self.assets["player_input"].get_pos(5, 5))
            pg.draw.rect(self.screen, AIVN.BLACK, self.assets["player_input"], 2, border_radius=AIVN.TEXTBOX_BORDER_RADIUS)

            self.screen.blit(self.assets["go_back_icon"].get_image(), self.assets["go_back_icon"].get_pos())
            return True




        self.screen.blit(self.assets[self.cur_NPC_loc].get_image(), self.assets[self.cur_NPC_loc].get_pos())
        self.screen.blit(self.assets["temp_NPC_sprite"].get_image(), self.assets["temp_NPC_sprite"].get_pos())

        # Render Player Input
        self.alpha_fill((100,100,100,180), self.assets["player_input"], border_radius=AIVN.TEXTBOX_BORDER_RADIUS)
        player_surface = self.assets["font"].render(self.cur_player_text, True, AIVN.BLACK)
        self.screen.blit(player_surface, self.assets["player_input"].get_pos(5, 5))
        pg.draw.rect(self.screen, AIVN.BLACK, self.assets["player_input"], 2, border_radius=AIVN.TEXTBOX_BORDER_RADIUS)

        # Render NPC Response
        self.alpha_fill((100,100,100,180), self.assets["NPC_response"], border_radius=AIVN.TEXTBOX_BORDER_RADIUS)
        NPC_surface = self.assets["font"].render(self.cur_NPC_text, True, AIVN.WHITE)
        self.screen.blit(NPC_surface, self.assets["NPC_response"].get_pos(5, 5))
        pg.draw.rect(self.screen, AIVN.BLACK, self.assets["NPC_response"], 2, border_radius=AIVN.TEXTBOX_BORDER_RADIUS)

        # Render all other components
        self.screen.blit(self.assets["go_back_icon"].get_image(), self.assets["go_back_icon"].get_pos())
        self.alpha_fill(AIVN.BLOOD, self.assets["kill_button"], border_radius=AIVN.BUTTON_BORDER_RADIUS)

        kill_text = self.assets["font"].render(f'Kill {self.cur_NPC.name}', True, AIVN.WHITE)
        self.screen.blit(kill_text, self.assets["kill_button"].get_pos(
                            (self.assets["kill_button"].width - kill_text.get_width()) // 2, 
                            (self.assets["kill_button"].height - kill_text.get_height()) // 2
                        )
        )

        return True






    def setup_win_loop(self):
        self.animation_queue.add_animation("fadeout", 3, speed=.5)

    def win_loop(self) -> None:
        # button = self.assets["restart_button"]

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            if event.type == pg.MOUSEBUTTONDOWN:
                # if button.collidepoint(event.pos):
                #     self.setup_map_loop(0)

                if AIVN.DEBUG:
                    print("Clicked within region at", event.pos)

        # Draw the background image
        self.screen.blit(self.assets["title_screen"].get_image(), self.assets["title_screen"].get_pos())
        self.alpha_fill((100,100,100,130), self.assets["title_screen"])

        # Render the title text
        title_text = self.assets["title_font"].render('You Found the Secret!', True, AIVN.WHITE)
        self.screen.blit(title_text, self.assets["title_text"].get_pos(-title_text.get_width() // 2, 0)) 

        # Render the Secret Word Text
        secret_phrase_text = self.assets["font"].render(f'The secret phrase was: {self.secret_word}', True, AIVN.BLACK)
        self.screen.blit(secret_phrase_text, self.assets["secret_phrase_text"].get_pos(-secret_phrase_text.get_width() // 2, 0))

        return True


    def lose_loop(self) -> None:
        pass


    

    def handle_animations(self) -> None:
        self.animation_queue.tick()
        if self.animation_queue.has_any_task_finished():
            task = self.animation_queue.get_finished_task()
            if task[0] == "fadeout":
                mapping = {0:1, 1:2, 2:1, 3:3, 4:4}
                self.cur_game_state = mapping[task[1]]
                if task[1] == 3:
                    self.animation_queue.add_animation("fadein", mapping[task[1]], speed=.5)
                else:
                    self.animation_queue.add_animation("fadein", mapping[task[1]])
            elif task[0] == "wait":
                self.setup_win_loop()
    

    def handle_music(self) -> None:
        # TODO: Clean this up
        if self.cur_game_state == 0 and self.cur_playing != "title":
            self.cur_playing = "title"
            pg.mixer.music.load(AIVN.TRACK_LIST[self.cur_playing])
            pg.mixer.music.play(-1)
        elif self.cur_game_state in [1, 2] and self.cur_playing != "main":
            self.cur_playing = "main"
            pg.mixer.music.load(AIVN.TRACK_LIST[self.cur_playing])
            pg.mixer.music.play(-1)
        elif self.cur_game_state == 3 and self.cur_playing != "win":
            self.cur_playing = "win"
            pg.mixer.music.load(AIVN.TRACK_LIST[self.cur_playing])
            pg.mixer.music.play(-1)




    def start_game_loop(self) -> None:
        running = True
        action_map = {
            0: self.title_loop, 
            1: self.map_loop, 
            2: self.NPC_loop,
            3: self.win_loop,
            4: self.lose_loop
        }
        while running:
            running = action_map[self.cur_game_state]()
            self.handle_animations()
            self.handle_music()
            # Show display after drawing everything
            pg.display.flip()

        # Quit Pygame
        pg.quit()



