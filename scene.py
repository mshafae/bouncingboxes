
import pygame
import rgbcolors
from more_itertools import grouper
from random import randint
from animation import Explosion

class Scene:
    def __init__(self, screen, background_color, soundtrack=None):
        self._screen = screen
        self._background = pygame.Surface(self._screen.get_size())
        self._background.fill(background_color)
        self._frame_rate = 60
        self._is_valid = True
        self._soundtrack = soundtrack
    
    def draw(self):
        self._screen.blit(self._background, (0, 0))
    
    def process_event(self, event):
        #print(str(event))
        if event.type == pygame.QUIT:
            print('Good Bye!')
            self._is_valid = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print('Bye bye!')
            self._is_valid = False            

    def is_valid(self):
        return self._is_valid
    
    def update(self):
        pass

    def start(self):
        if self._soundtrack:
            try:
                pygame.mixer.music.load(self._soundtrack)
            except pygame.error:
                print('Cannot open the mixer?')
                raise SystemExit('broken!!')
            pygame.mixer.music.play(-1)

    def end(self):
        if self._soundtrack:
            pygame.mixer.music.stop()
    
    def frame_rate(self):
        return self._frame_rate

class EmptyPressAnyKeyScene(Scene):
    def __init__(self, screen, background_color, soundtrack=None):
        super().__init__(screen, background_color, soundtrack)
        self._words_per_line = 5
        
    def draw(self):
        super().draw()

    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame.KEYUP:
            self._is_valid = False

class BlinkingTitle(Scene):
    def __init__(self, screen, message, color, size, background_color, soundtrack=None):
        super().__init__(screen, background_color, soundtrack)
        self._message_color = color
        self._message_complement_color = (255 - color[0], 255 - color[1], 255 - color[2])
        self._size = size
        self._message = message
        self._t = 0.0
        self._delta_t = 0.01
    
    def _interpolate(self):
        self._t += self._delta_t
        if self._t > 1.0 or self._t < 0.0:
            self._delta_t *= -1
        c = rgbcolors.sum_color(rgbcolors.mult_color((1.0 - self._t), self._message_complement_color), rgbcolors.mult_color(self._t, self._message_color))
        return c
    
    def draw(self):
        super().draw()
        presskey_font = pygame.font.Font(pygame.font.get_default_font(), self._size)
        presskey = presskey_font.render(self._message, True, self._interpolate())
        (w, h) = self._screen.get_size()
        presskey_pos = presskey.get_rect(center=(w/2, h/2))
        press_any_key_font = pygame.font.Font(pygame.font.get_default_font(), 18)
        press_any_key = press_any_key_font.render('Press any key.', True, rgbcolors.black)
        (w, h) = self._screen.get_size()
        press_any_key_pos = press_any_key.get_rect(center=(w/2, h - 50))
        self._screen.blit(presskey, presskey_pos)
        self._screen.blit(press_any_key, press_any_key_pos)

    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame.KEYUP:
            self._is_valid = False

class TitleScene(Scene):
    def __init__(self, screen, title, title_color, title_size, soundtrack=None):
        super().__init__(screen, rgbcolors.pink, soundtrack)
        title_font = pygame.font.Font(pygame.font.get_default_font(), title_size)
        self._title = title_font.render(title, True, title_color)
        press_any_key_font = pygame.font.Font(pygame.font.get_default_font(), 18)
        self._press_any_key = press_any_key_font.render('Press any key.', True, rgbcolors.black)
        (w, h) = self._screen.get_size()
        self._title_pos = self._title.get_rect(center=(w/2, h/2))
        self._press_any_key_pos = self._press_any_key.get_rect(center=(w/2, h - 50))
    
    def draw(self):
        super().draw()
        self._screen.blit(self._title, self._title_pos)
        self._screen.blit(self._press_any_key, self._press_any_key_pos)
    
    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame.KEYDOWN:
            self._is_valid = False

class BouncingBoxesScene(Scene):
    def __init__(self, boxes, screen, background_color, frame_rate, soundtrack=None):
        super().__init__(screen, background_color, soundtrack)
        self._boxes = boxes
        self._screen = screen
        self._frame_rate = frame_rate
        (w, h) = self._screen.get_size()
        self._boundary_rect = pygame.Rect((0, 0), (w, h))

    def _draw_boundaries(self):
        (w, h) = self._screen.get_size()
        pygame.draw.rect(self._screen, rgbcolors.yellow, self._boundary_rect, (w//100), (w//200))

    def process_event(self, event):
        super().process_event(event)

    def draw(self):
        super().draw()
        self._draw_boundaries()
        for box in self._boxes:
            pygame.draw.rect(self._screen, box.color, box.rect)


    def update(self):
        super().update()
        for box in self._boxes:
            box.update()
        for index, box in enumerate(self._boxes):
            if not pygame.Rect.contains(self._boundary_rect, box.rect):
                box.reflect(self._boundary_rect.left, self._boundary_rect.left + self._boundary_rect.width, self._boundary_rect.top, self._boundary_rect.top + self._boundary_rect.height)
            else:
                for other_box in self._boxes[index+1:]:
                    if pygame.Rect.colliderect(box.rect, other_box.rect):
                        # print(box.id, other_box.id)
                        if box.bounce():
                            Explosion(box)
                        if other_box.bounce():
                            Explosion(other_box)

