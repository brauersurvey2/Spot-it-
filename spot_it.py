####################################################################
#   Spot it! Project
#       by Hans Brauer
#  
#   Algorithm
#       create deck of Spot it! cards
#       allow user to play games involving finding matching symbols
####################################################################

import pygame as pg
import random
from library import *
from sprites import *
from pygame import gfxdraw
import sys

class Game:
    def __init__(self):
        # initialize game window
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption(title)
        self.clock = pg.time.Clock()
        self.font_name = pg.font.match_font(font_name)
        self.game_code = 'm'
        self.rf_records = {8:0, 15:0, "inf":0}

    def new(self):
        # start a new game
        self.deck = SiDeck()
        self.cards = []
        self.card_sprites = pg.sprite.Group()
        self.symbol_sprites = pg.sprite.Group()
        self.correct_matches = 0
        self.circuit_complete = False
        self.time = ''
        self.first_card = ''
        self.first_selection = True
        self.ready = False
        self.time_left = ''
        self.start = pg.time.get_ticks()
        self.instructions(self.game_code)

    def instructions(self, game_code):
        # display instructions for specific game mode
        while not self.time:
            self.event_lst = pg.event.get()
            for event in self.event_lst:
                self.check_for_window_close(event)
            self.clock.tick(FPS)
            self.screen.fill(teal)
            self.draw_text(instructions_dict[game_code]["title"], 60, (width // 2, height // 10))
            counter = 0
            if self.game_code == 'rf':
                start = height // 4
                size = 24
            else:
                start = height // 5
                size = 22
            for num, line in enumerate(instructions_dict[game_code]["instructions"]):
                if len(line) == 0:
                    counter += 15
                else:
                    self.draw_text(line, size, (width // 2, start + num * size - counter))
            
            self.draw_text("Select an amount of time to find each match:", 35, (width // 2, height * 2 // 3))
            
            eight_sec_button = pg.Rect(0, 0, 150, 75)
            fifteen_sec_button = pg.Rect(0, 0, 150, 75)
            inf_button = pg.Rect(0, 0, 150, 75)
            inf_button.center = (width // 6, height * 5 // 6)
            fifteen_sec_button.center = (width // 2, height * 5 // 6)
            eight_sec_button.center = (width * 5 // 6, height * 5 // 6)

            self.time = self.button(eight_sec_button, dark_red, red, self.time, 8, "8 Seconds")
            self.time = self.button(fifteen_sec_button, dark_red, red, self.time, 15, "15 Seconds")
            self.time = self.button(inf_button, dark_red, red, self.time, "inf", "Unlimited Time")

            if self.time != "inf":
                self.time_left = self.time * 1000

            pg.display.flip()
        pg.mixer.music.stop()

    def wait_for_sfx(self):
        while pg.mixer.get_busy():
            self.clock.tick(FPS)
            self.event_lst = pg.event.get()
            for event in self.event_lst:
                self.check_for_window_close(event)

    def run(self):
        # game loop
        self.wait_for_sfx()
        pg.mixer.music.load(game_music)
        pg.mixer.music.set_volume(.2)
        pg.mixer.music.play(loops = -1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        # pause for a bit when a round ends
        pg.mixer.music.stop()
        end = pg.time.get_ticks()
        while pg.time.get_ticks() - end < 1500:
            self.clock.tick(FPS)
            self.event_lst = pg.event.get()
            for event in self.event_lst:
                self.check_for_window_close(event)

    def events(self):
        # game loop - events
        self.event_lst = pg.event.get()
        self.symbol_selection = ''
        self.click = False
        now = pg.time.get_ticks()
        stagger = 0
        if self.time_left != '':
            self.time_left = self.start + 1000 * self.time - now
            if not self.ready:
                self.time_left = self.time * 1000
                self.start = now
            if self.time_left < 0:
                pg.mixer.Sound(incorrect_sfx).play()
                self.time_left = 0
                self.playing = False
            
        if len(self.cards) == 0:
            c = CardSprite(self.deck.deck.pop(random.randint(0, len(self.deck.deck) - 1)), width * 5 // 4, height // 2, 1)
            stagger = width // 2
            self.cards.append(c.values)
            self.card_sprites.add(c)
            for symbol in c.symbols:
                self.symbol_sprites.add(symbol)

        if len(self.cards) == 1:
            c = CardSprite(self.deck.deck.pop(random.randint(0, len(self.deck.deck) - 1)), width * 5 // 4 + stagger, height // 2)
            self.cards.append(c.values)
            self.card_sprites.add(c)
            for symbol in c.symbols:
                self.symbol_sprites.add(symbol)

        self.ready = True
        for card in self.card_sprites:
            if not card.ready:
                self.ready = False

        for event in self.event_lst:
            self.check_for_window_close(event)
            if event.type == pg.MOUSEBUTTONUP and self.ready:
                self.click = True

        if self.ready:
            for symbol in self.symbol_sprites:
                self.symbol_selection = symbol.button(self.click, self.symbol_selection)

        if self.symbol_selection != '':
            self.ready = False
            if self.symbol_selection in set(self.cards[0]) & set(self.cards[1]):
                pg.mixer.Sound(correct_sfx).play()
                self.correct_matches += 1
                if self.game_code == 'c':
                    c = self.cards.pop(0)
                    if self.first_selection and not self.first_card:
                        self.first_card = c
                        self.first_selection = False
                    if len(self.deck.deck) == 0:
                        if self.first_card:
                            self.deck.deck.append(self.first_card)
                            self.first_card = ""
                        else:
                            self.playing = False
                            if self.time_left != '':
                                self.time_left = self.time * 1000
                            self.circuit_complete = True
                    for card in self.card_sprites:
                        if card.values == c:
                            card.new_state(2)
                        else:
                            card.new_state(1)
                elif self.game_code == 'rf':
                    for i in range(2):
                        self.deck.deck.append(self.cards.pop(0))
                    for card in self.card_sprites:
                        card.new_state(2)
            else:
                pg.mixer.Sound(incorrect_sfx).play()
                self.playing = False
                if self.time_left != '':
                    self.time_left = 0

    def update(self):
        # game loop - update
        if self.playing:
            self.card_sprites.update()

    def draw_circle(self, center, radius, color):
        gfxdraw.aacircle(self.screen, center[0], center[1], radius, color)
        gfxdraw.filled_circle(self.screen, center[0], center[1], radius, color)

    def draw(self):
        # game loop - draw
        self.screen.fill(teal)
        self.draw_text(f'Correct Matches: {self.correct_matches}', 30, (width // 4, height // 10))
        self.card_sprites.draw(self.screen)
        if self.time_left != '':
            self.draw_text("{:<17}".format(f"Time Left: {'{:.2f}'.format(self.time_left / 1000)}"), 30, (width * 3 // 4 - 100, height // 10), "midleft")
        if self.playing and self.ready:
            for symbol in self.symbol_sprites:
                if symbol.hover:
                    self.draw_circle(symbol.rect.center, symbol.rect.height * 2 // 3, green)
        if len(self.deck.deck) == 0 and not self.first_card:
            self.draw_text("Last Card!", 75, (width // 2, height * 9 // 10))
        self.symbol_sprites.draw(self.screen)
        pg.display.flip()

    def check_for_window_close(self, event):
        # close window if user clicks x
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    def show_main_menu(self):
        # main menu with game options
        if not pg.mixer.music.get_busy():
            pg.mixer.music.load(menu_music)
            pg.mixer.music.set_volume(.4)
            pg.mixer.music.play(loops = -1)
        self.game_code = ""
        while not self.game_code:
            self.event_lst = pg.event.get()
            for event in self.event_lst:
                self.check_for_window_close(event)
            self.clock.tick(FPS)
            self.screen.fill(teal)
            self.draw_text(title, 100, (width // 2, height // 4))
            
            # buttons for game modes
            c_button = pg.Rect(0, 0, 150, 75)
            rf_button = pg.Rect(0, 0, 150, 75)
            c_button.center = (width // 4, height * 2 // 3)
            rf_button.center = (width * 3 // 4, height * 2 // 3)

            self.game_code = self.button(c_button, dark_red, red, \
            self.game_code, 'c', "Circuit", "Game Mode")
            self.game_code = self.button(rf_button, dark_red, red, \
            self.game_code, 'rf', "Rapid Fire", "Game Mode")

            pg.display.flip()
        self.wait_for_sfx()

    def show_go_screen(self):
        # game over/continue
        if self.game_code == 'rf' and self.correct_matches > self.rf_records[self.time]:
            self.rf_records[self.time] = self.correct_matches
            new_record = True
        else:
            new_record = False

        if new_record or self.circuit_complete:
            pg.mixer.Sound(success_sfx).play()
        self.wait_for_sfx()
        pg.mixer.music.load(menu_music)
        pg.mixer.music.set_volume(.4)
        pg.mixer.music.play(loops = -1)
        
        last_code = self.game_code
        self.game_code = ""
        while not self.game_code:
            self.event_lst = pg.event.get()
            for event in self.event_lst:
                self.check_for_window_close(event)
            self.clock.tick(FPS)
            self.screen.fill(teal)
            if self.circuit_complete:
                self.draw_text("Circuit Complete!", 75, (width // 2, height // 6))
            elif new_record:
                self.draw_text("New Record!", 100, (width // 2, height // 6))
                self.draw_text(mode_msg[self.time], 40, (width // 2, height // 6 + 70))
            else:
                self.draw_text("Game Over", 100, (width // 2, height // 6))
            
            if last_code == 'rf' and not new_record:
                self.draw_text(f"Correct Matches: {self.correct_matches}", 35, (width // 2, height * 2 // 5))
                self.draw_text(f"Current Record {mode_msg[self.time]}: {self.rf_records[self.time]}", 35, (width // 2, height // 2))
            else:
                self.draw_text(f"Correct Matches: {self.correct_matches}", 35, (width // 2, height // 2))
         
            # buttons for game modes
            r_button = pg.Rect(0, 0, 150, 75)
            m_button = pg.Rect(0, 0, 150, 75)
            r_button.center = (width // 4, height * 5 // 6)
            m_button.center = (width * 3 // 4, height * 5 // 6)

            if last_code == 'c':
                self.game_code = self.button(r_button, dark_red, red, self.game_code, \
                last_code, "Play Circuit", "Mode Again")
            elif last_code == 'rf':
                self.game_code = self.button(r_button, dark_red, red, self.game_code, \
                last_code, "Play Rapid Fire", "Mode Again")
            self.game_code = self.button(m_button, dark_red, red, self.game_code, \
            'm', "Return to", "Main Menu")

            pg.display.flip()
        self.wait_for_sfx()

    def button(self, button, original_color, hover_color, old_code, new_code, *text_tuple):
        # display button that changes color if mouse hovers over it
        # returns new game code if button is clicked
        mouse = pg.mouse.get_pos()
        clicked = False

        if button.left < mouse[0] < button.right \
        and button.top < mouse[1] < button.bottom:
            for event in self.event_lst:
                if event.type == pg.MOUSEBUTTONUP:
                    clicked = True
            pg.draw.rect(self.screen, hover_color, button)
        else:
            pg.draw.rect(self.screen, original_color, button)
        
        if len(text_tuple) > 0:
            for num, line in enumerate(text_tuple):
                self.draw_text(line, 24, (button.centerx, button.top + \
                button.height * (num + 1) // (len(text_tuple) + 1)))

        if clicked:
            pg.mixer.Sound(click_sfx).play()
            return new_code
        else:
            return old_code

    def draw_text(self, text, size, center, point = "center", color = white):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if point == "center":
            text_rect.center = center
        elif point == "midleft":
            text_rect.midleft = center
        self.screen.blit(text_surface, text_rect)

def play():
    g = Game()
    
    while True:
        if g.game_code == 'm':
            g.show_main_menu()
        g.new()
        g.run()
        g.show_go_screen()
    
if __name__ == "__main__":
    play()