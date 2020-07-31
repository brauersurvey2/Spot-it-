import pygame as pg
from library import *
import random

class SiDeck:
    def __init__(self, n = 7):
        self.deck = []

        for i in range(n+1):
            self.deck.append([0] + [1 + n * i + k for k in range(n)])

        for i in range(n):
            for j in range(n):
                self.deck.append([i + 1] + [1 + n + n * k + (j - i * k) % n for k in range(n)])

        for card in self.deck:
            random.shuffle(card)
        random.shuffle(self.deck)

class CardSprite(pg.sprite.Sprite):
    def __init__(self, card, x, y, state = 0):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((200, 280))
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vx = 0
        self.state = state
        self.values = card
        self.symbols = []
        self.ready = False
        for num, symbol in enumerate(card):
            s = SymbolSprite(self, symbol, num, len(card))
            self.symbols.append(s)

    def new_state(self, state):
        self.state = state
        self.ready = False

    def update(self):
        if self.state == 0:
            self.vx = -10
            if self.rect.centerx <= width * 3 // 4:
                self.ready = True
                self.vx = width * 3 // 4 - self.rect.centerx
        elif self.state == 1:
            self.vx = -10
            if self.rect.centerx <= width // 4:
                self.ready = True
                self.vx = width // 4 - self.rect.centerx
        elif self.state == 2:
            self.vx = -10
            if self.rect.right < 0:
                self.kill()
                for symbol in self.symbols:
                    symbol.kill()

        self.rect.x += self.vx
        for symbol in self.symbols:
            symbol.update(self.vx)

class SymbolSprite(pg.sprite.Sprite):
    def __init__(self, card, value, position, total):
        pg.sprite.Sprite.__init__(self)
        self.value = value
        self.orig_image = icons_lst[value].convert_alpha()
        self.rect = self.orig_image.get_rect()
        self.image = pg.transform.smoothscale(self.orig_image, tuple(card.rect.height * 3 * dim // (2 * total* self.rect.height) for dim in (self.rect.width, self.rect.height)))
        self.image.set_colorkey(white)
        self.rect = self.image.get_rect()
        self.hover = False
        row_height = 3 * card.rect.height // (2 * total)
        num_rows = total // 2 + total % 2
        row_margin = (card.rect.height - row_height * num_rows) // (num_rows + 1)
        y_location = card.rect.top + row_margin * (position // 2 + 1) + row_height * (position // 2)
        self.rect.top = y_location
        if position % 2 == 0:
            self.rect.centerx = card.rect.left + card.rect.width * 3 // 10
        elif position % 2 == 1:
            self.rect.centerx = card.rect.right - card.rect.width * 3 // 10
        
    def button(self, click, old_code):
        # outlines symbol if mouse hovers over it
        # returns symbol's value if symbol is clicked
        mouse = pg.mouse.get_pos()
        self.hover = False

        if self.rect.left < mouse[0] < self.rect.right \
        and self.rect.top < mouse[1] < self.rect.bottom:
            self.hover = True
            if click:
                return self.value
        
        return old_code
        
    def update(self, vx):
        self.rect.x += vx