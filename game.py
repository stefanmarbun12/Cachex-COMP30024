"""
COMP30024 Artificial Intelligence, Semester 1, 2022
Testing tool for Project Part B
Extension on https://github.com/ANDREYDEN/Hex-Game for Cachex, by Stefan Marbun
Please use this code for testing purposes only, do not copy anything directly to use in your project submission
"""

import pygame as pg
import sys
from os import path
from funcs import *
from button import *
from player import Player


class Game:
    def __init__(self, size, with_ai, sound_state):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((W, H))
        self.clock = pg.time.Clock()
        self.size = size
        self.tile_size = 0
        self.set_tile_size()
        self.state = [[0 for _ in range(self.size)] for __ in range(self.size)]
        self.origin = Point(W / 2 - self.tile_size * size, H - self.tile_size * size * 0.75)
        self.move = 1
        self.started = False
        self.sound_state = sound_state

        self.with_ai = with_ai
        self.AI = Player("blue", size) if with_ai else None
        self.first_move = None
        self.second_move = False
        self.last_move = None

    def load_data(self):
        """Load all the data (images, files, etc)"""
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        doc_folder = path.join(game_folder, 'docs')

        self.bg_img = pg.image.load(path.join(img_folder, BG_IMG)).convert_alpha()
        self.pause_img = pg.image.load(path.join(img_folder, PAUSE_IMG)).convert_alpha()
        self.back_img = pg.image.load(path.join(img_folder, BACK_IMG)).convert_alpha()
        self.up_img = pg.image.load(path.join(img_folder, UP_IMG)).convert_alpha()
        self.down_img = pg.image.load(path.join(img_folder, DOWN_IMG)).convert_alpha()

        # ------------------MUSIC--------------------
        self.click_sound = pg.mixer.Sound(path.join(doc_folder, CLICK_SOUND))
        self.click_sound_channel = pg.mixer.Channel(2)

        # -----------------TEXT--------------------
        with open(path.join(doc_folder, RULES), 'r') as f:
            self.rules_text = ''.join(f.readlines())

    def set_tile_size(self):
        if self.size < 6:
            self.tile_size = 3 * (H / 2 - 50) / 3 / sqrt(3) / (self.size - 1)
        else:
            self.tile_size = 4 * (H / 2 - 50) / 3 / sqrt(3) / (self.size - 1)

    def get_coord(self, r, c):
        """Translates grid coordinates to real coordinates"""
        x = self.origin.x + (r + 2 * c) * self.tile_size * sqrt(3) / 2
        y = self.origin.y - r * 3 / 2 * self.tile_size
        return int(x), int(y)

    def tick(self, pos):
        """Is called if mouse pressed, changes the state of the game"""
        for r in range(self.size):
            for c in range(self.size):
                x, y = self.get_coord(r, c)
                if in_hex(pos, x, y, self.tile_size) and self.state[r][c] != 2 and self.state[r][c] != 1:
                    if self.sound_state:
                        self.click_sound_channel.play(self.click_sound)

                    # prevent center tile as first move
                    if (self.first_move is None) and self.size % 2 == 1 and r == self.size // 2 and c == self.size // 2:
                        return

                    self.validate_move(r, c)
                    if self.check_win():
                        return

                    # AI opponent's next turn
                    if self.AI:
                        self.AI.turn("red", ("PLACE", r, c))
                        print(f"Updated state with ({r},{c})")
                        action = self.AI.action()
                        move_type = action[0]
                        if move_type == "PLACE":
                            next_r = action[1]
                            next_c = action[2]
                        elif move_type == "STEAL":
                            next_r = self.first_move[1]
                            next_c = self.first_move[0]
                        else:
                            print(f"Invalid move from AI opponent: ({action})!")
                            sys.exit()

                        self.validate_move(next_r, next_c)

                        if move_type == "PLACE":
                            self.AI.turn("blue", ("PLACE", next_r, next_c))
                            print(f"Updated state with ({next_r},{next_c})")
                        elif move_type == "STEAL":
                            self.AI.turn("blue", ("STEAL",))
                            print(f"Updated state with steal")
                    return

    def validate_move(self, r, c):
        """Updates game state with the new move if all checks pass"""
        if (not (0 <= r < self.size and 0 <= c < self.size)) or self.state[r][c] == 2 or self.state[r][c] == 1:
            print(f"({r},{c}) is an invalid move!")
            sys.exit()

        self.state[r][c] = self.move
        self.last_move = (r, c)
        self.check_diamond(r, c, self.move)
        self.move = 3 - self.move

        # check for steal
        if self.second_move:
            self.second_move = False
            if (c, r) == self.first_move:
                self.state[c][r] = 0

        if self.first_move is None:
            self.first_move = (r, c)
            self.second_move = True

    def check_diamond(self, r, c, player):
        to_clear = []
        for cells in self.generate_valid_diamonds(r, c):
            up = self.state[cells[0][0]][cells[0][1]]
            down = self.state[cells[1][0]][cells[1][1]]
            left = self.state[cells[2][0]][cells[2][1]]
            right = self.state[cells[3][0]][cells[3][1]]
            if up == down and left == right and up != left:
                if up == player or down == player:
                    to_clear.append(cells[2])
                    to_clear.append(cells[3])
                if left == player or right == player:
                    to_clear.append(cells[0])
                    to_clear.append(cells[1])
        for cell in to_clear:
            self.state[cell[0]][cell[1]] = 0

    def generate_valid_diamonds(self, r, c):
        valid_diamonds = []
        for cells in POSSIBLE_DIAMONDS:
            valid_diamond = []
            invalid = False
            for (x, y) in cells:
                if 0 <= (x + r) < self.size and 0 <= (y + c) < self.size:
                    valid_diamond.append((x + r, y + c))
                else:
                    invalid = True
                    break
            if not invalid:
                valid_diamonds.append(valid_diamond)
        return valid_diamonds

    def highlight(self, pos):
        """Highlights the hexagon that is under the mouse"""
        for r in range(self.size):
            for c in range(self.size):
                x, y = self.get_coord(r, c)
                if self.state[r][c] == 0 and in_hex(pos, x, y, self.tile_size):
                    self.state[r][c] = self.move + 2
                elif self.state[r][c] > 2 and not in_hex(pos, x, y, self.tile_size):
                    self.state[r][c] = 0

    def show_grid(self):
        """shows hexagonal grid as well as players moves and destination sides"""
        # show turn info
        if self.move == 2:
            if self.last_move:
                text_out(self.screen, f"Red placed at ({self.last_move[0]},{self.last_move[1]})",
                         20, RED, (W / 2, 0.25 * H / 8))
            text_out(self.screen, "Blue's turn", 20, LIGHT_BLUE, (W / 2, 0.75 * H / 8))
        elif self.move == 1:
            if self.last_move:
                text_out(self.screen, f"Blue placed at ({self.last_move[0]},{self.last_move[1]})",
                         20, LIGHT_BLUE, (W / 2, 0.25 * H / 8))
            text_out(self.screen, "Red's turn", 20, RED, (W / 2, 0.6 * H / 8))

        if self.started:
            for r in range(self.size):
                for c in range(self.size):
                    x, y = self.get_coord(r, c)
                    # draw players
                    if self.state[r][c] == 1:
                        draw_hex(self.screen, RED, BLACK, (x, y), self.tile_size, r, c, self.size)
                    elif self.state[r][c] == 2:
                        draw_hex(self.screen, BLUE, BLACK, (x, y), self.tile_size, r, c, self.size)
                    elif self.state[r][c] == 3:
                        draw_hex(self.screen, LIGHT_RED, BLACK, (x, y), self.tile_size, r, c, self.size)
                    elif self.state[r][c] == 4:
                        draw_hex(self.screen, LIGHT_BLUE, BLACK, (x, y), self.tile_size, r, c, self.size)
                    else:
                        draw_hex(self.screen, WHITE, BLACK, (x, y), self.tile_size, r, c, self.size)

    def check_win(self):
        """checks if any of the players have won"""
        for y in range(self.size):
            if self.state[y][0] == 2:
                if dfs(Point(y, 0), self.state, lambda v: (v.Y == self.size - 1), 2):
                    return 2

        for x in range(self.size):
            if self.state[0][x] == 1:
                if dfs(Point(0, x), self.state, lambda v: (v.X == self.size - 1), 1):
                    return 1
        return 0

    def shadow(self):
        shadow = pg.Surface((W, H))
        shadow.set_alpha(1000)
        self.screen.blit(shadow, (0, 0))

    def start_screen(self):
        """Shows start screen, returns True if the game has started"""
        start = True
        # initializing buttons
        play = Button((W / 2, 2 * H / 3), 80, 'Play')
        settings = Button((150, H - 75), 50, 'Settings')
        rules = Button((W - 100, H - 75), 50, 'Rules')
        buttons = [play, settings, rules]
        while start:
            # sticking to fps
            self.clock.tick(FPS)
            # --------------------EVENTS---------------------
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # if exit button is pressed
                    return False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # if mouse is pressed check button overlapping
                    if play.triggered(channel=self.click_sound_channel,
                                      sound=self.click_sound,
                                      playing=self.sound_state):
                        self.__init__(self.size, self.with_ai, self.sound_state)
                        self.started = True
                        return True
                    if rules.triggered(channel=self.click_sound_channel,
                                       sound=self.click_sound,
                                       playing=self.sound_state):
                        start = self.rules_screen()
                    if settings.triggered(channel=self.click_sound_channel,
                                          sound=self.click_sound,
                                          playing=self.sound_state):
                        start = self.settings_screen()
            # highlight buttons
            for button in buttons:
                button.highlighted()
            # --------------------STUFF-----------------------
            self.screen.blit(self.bg_img, (0, 0))
            text_out(self.screen, 'CACHEX', 100, WHITE, (W / 2, H / 3))
            text_out(self.screen, 'because algorithms are fun!', 30, ORANGE, (W / 2, 1.4 * H / 3))
            # show buttons
            for button in buttons:
                button.show(self.screen)
            # double processing
            pg.display.flip()

    def rules_screen(self):
        """Shows the rules of the game, returns True if the "back" button was hit"""
        start = True
        # initializing buttons
        back = Button((30, 30), 50, img=self.back_img)
        buttons = [back]
        while start:
            # sticking to fps
            self.clock.tick(FPS)
            # --------------------EVENTS---------------------
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # if exit button is pressed
                    return False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # if mouse is pressed check button overlapping
                    if back.triggered(channel=self.click_sound_channel,
                                      sound=self.click_sound,
                                      playing=self.sound_state):
                        return True
            # highlight buttons
            for button in buttons:
                button.highlighted()
            # --------------------STUFF-----------------------
            self.screen.blit(self.bg_img, (0, 0))
            text_out(self.screen, 'Rules', 100, ORANGE, (W / 2, H / 3))
            text_out_multiline(self.screen, self.rules_text, 30, WHITE, (W / 2, H / 3))
            # show buttons
            for button in buttons:
                button.show(self.screen)
            # double processing
            pg.display.flip()

    def settings_screen(self):
        """Shows the rules of the game, returns True if the "back" button was hit"""
        start = True
        # initializing buttons
        back = Button((30, 30), 50, img=self.back_img)
        up = Button((2 * W / 3 + 60, H / 2 - 25), 50, img=self.up_img)
        down = Button((2 * W / 3 + 60, H / 2 + 25), 50, img=self.down_img)
        sound_state = 'On' if self.sound_state else 'Off'
        ai_state = 'Yes' if self.with_ai else 'No'
        ai_switch = Button((2 * W / 3, H / 2 + 60), 50, ai_state, col=RED)
        sound_switch = Button((2 * W / 3 - 50, H / 2 + 120), 50, sound_state, col=RED)
        buttons = [back, up, down, ai_switch, sound_switch]
        while start:
            # sticking to fps
            self.clock.tick(FPS)
            # --------------------EVENTS---------------------
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # if exit button is pressed
                    return False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # if mouse is pressed check button overlapping
                    if back.triggered(channel=self.click_sound_channel,
                                      sound=self.click_sound,
                                      playing=self.sound_state):
                        return True
                    if up.triggered(channel=self.click_sound_channel,
                                    sound=self.click_sound,
                                    playing=self.sound_state):
                        self.size = min(MAX_BOARD_SIZE, self.size + 1)
                    if down.triggered(channel=self.click_sound_channel,
                                      sound=self.click_sound,
                                      playing=self.sound_state):
                        self.size = max(MIN_BOARD_SIZE, self.size - 1)
                    if ai_switch.triggered(channel=self.click_sound_channel,
                                           sound=self.click_sound,
                                           playing=self.sound_state):
                        if ai_switch.text == 'Yes':
                            self.with_ai = False
                            ai_switch.text = 'No'
                        else:
                            self.with_ai = True
                            ai_switch.text = 'Yes'
                    if sound_switch.triggered(channel=self.click_sound_channel,
                                              sound=self.click_sound,
                                              playing=self.sound_state):
                        if sound_switch.text == 'On':
                            self.sound_state = False
                            sound_switch.text = 'Off'
                        else:
                            self.sound_state = True
                            sound_switch.text = 'On'
            # highlight buttons
            for button in buttons:
                button.highlighted()
            # --------------------STUFF-----------------------
            self.screen.blit(self.bg_img, (0, 0))
            text_out(self.screen, 'Settings', 100, ORANGE, (W / 2, H / 4))
            text_out(self.screen, 'Board size:', 50, WHITE, (W / 3, H / 2))
            text_out(self.screen, self.size, 50, WHITE, (2 * W / 3, H / 2))
            text_out(self.screen, 'Against AI:', 50, WHITE, (W / 3, H / 2 + 60))
            text_out(self.screen, 'Sound:', 50, WHITE, (W / 3, H / 2 + 120))

            # show buttons
            for button in buttons:
                button.show(self.screen)
            # double processing
            pg.display.flip()

    def pause_screen(self):
        """Shows pause screen, returns True if the game was resumed"""
        start = True
        # initializing buttons
        resume = Button((W / 2, H / 3), 80, 'Resume', col=WHITE)
        home = Button((W / 2, H / 2), 50, 'Home', col=WHITE)
        buttons = [home, resume]
        while start:
            # sticking to fps
            self.clock.tick(FPS)
            # --------------------EVENTS---------------------
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # if exit button is pressed
                    return False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # if mouse is pressed check button overlapping
                    if home.triggered(channel=self.click_sound_channel,
                                      sound=self.click_sound,
                                      playing=self.sound_state):
                        self.started = False
                        return True
                    if resume.triggered(channel=self.click_sound_channel,
                                        sound=self.click_sound,
                                        playing=self.sound_state):
                        return True
            # highlight buttons
            for button in buttons:
                button.highlighted()
            # --------------------STUFF-----------------------
            # show buttons
            self.screen.blit(self.bg_img, (0, 0))
            # self.showGrid()
            self.shadow()
            for button in buttons:
                button.show(self.screen)
            # double processing
            pg.display.flip()

    def game_over_screen(self, winner):
        """Shows game over screen, returns True if any key is hit"""
        go = True
        home = Button((3 * W / 4, 7 * H / 8), 40, 'Home', col=WHITE)
        while go:
            # sticking to fps
            self.clock.tick(FPS)
            # --------------------EVENTS---------------------
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # if exit button is pressed
                    return False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # if mouse is pressed check button overlapping
                    if home.triggered(channel=self.click_sound_channel,
                                      sound=self.click_sound,
                                      playing=self.sound_state):
                        self.started = False
                        return True
            home.highlighted()
            # --------------------STUFF-----------------------
            self.screen.blit(self.bg_img, (0, 0))
            self.show_grid()
            self.shadow()
            text_out(self.screen, 'GAME OVER', 40, WHITE, (W / 4, 7 * H / 8))
            if winner == 2:
                text_out(self.screen, 'Blue won', 20, LIGHT_BLUE, (W / 4, 7.5 * H / 8))
            else:
                text_out(self.screen, 'Red won', 20, RED, (W / 4, 7.5 * H / 8))
            home.show(self.screen)
            # double processing
            pg.display.flip()
