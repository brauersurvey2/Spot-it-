import os
import pygame as pg
import random

#display settings
title = "Spot it!"
width = 600
height = 480
FPS = 60
font_name = "arial"

# define colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
dark_red = (225, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
teal = (0, 200, 200)

# game folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")
sfx_folder = os.path.join(game_folder, "sfx")
icons_lst = []
for i in range(57):
    icons_lst.append(pg.image.load(os.path.join(img_folder, "icon" + str(i) + ".png")))
random.shuffle(icons_lst)
menu_music = os.path.join(sfx_folder, "Fun Bass Loop.ogg")
game_music = os.path.join(sfx_folder, "bensound-ukulele.mp3")
# royalty-free music from bensound.com
click_sfx = os.path.join(sfx_folder, "Click.wav")
success_sfx = os.path.join(sfx_folder, "Success.wav")
correct_sfx = os.path.join(sfx_folder, "Correct.wav")
incorrect_sfx = os.path.join(sfx_folder, "Incorrect.wav")

instructions_dict = {"c": {"title": "Circuit Game Mode", \
"instructions": ["A deck of 57 cards will be generated", "", \
"2 cards will appear on the screen", \
"On either card, click the one symbol that both cards share", "", \
"After each correct match, one card will go away,", \
"and one new card will come in", "", \
"The game ends when you make an incorrect match,", \
"or you work your way around the circuit by eventually", \
"matching the last card with the original first card"]}, \
"rf": {"title": "Rapid Fire Game Mode", \
"instructions": ["2 randomly selected cards will appear on the screen", "", \
"On either card, click the one symbol that both cards share", "", \
"After each correct match, two new cards will appear", "", \
"The game ends when you make an incorrect match"]}}

mode_msg = {8: "for 8 Second Time Mode", 15: "for 15 Second Time Mode", "inf": "for Unlimited Time Mode"}