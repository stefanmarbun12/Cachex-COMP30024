"""
COMP30024 Artificial Intelligence, Semester 1, 2022
Testing tool for Project Part B
Extension on https://github.com/ANDREYDEN/Hex-Game for Cachex, by Stefan Marbun
Please use this code for testing purposes only, do not copy anything directly to use in your project submission
"""

from game import *
from funcs import *
import pygame as pg

game = Game(SIZE, True, True)
game.load_data()

# button initializing
pause = Button((30, 30), 50, img=game.pause_img)
buttons = [pause]

pg.display.set_caption('Cachex the Game')

# draw()
run = True
while run:
    # sticking to fps
    game.clock.tick(FPS)
    if not game.started:
        run = game.start_screen()
    else:
        # --------------------EVENTS---------------------
        game.highlight(pg.mouse.get_pos())
        for event in pg.event.get():
            if event.type == pg.QUIT:
                # if exit button is pressed
                run = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                # the players move
                game.tick(pg.mouse.get_pos())
                if pause.triggered(channel=game.click_sound_channel,
                                   sound=game.click_sound,
                                   playing=game.sound_state):
                    run = game.pause_screen()

        # highlight buttons
        for button in buttons:
            button.highlighted()

        # --------------------STUFF-----------------------
        game.screen.blit(game.bg_img, (0, 0))
        game.show_grid()
        for button in buttons:
            button.show(game.screen)
        if game.check_win():
            run = game.game_over_screen(game.check_win())
    # double processing
    pg.display.flip()

pg.quit()
