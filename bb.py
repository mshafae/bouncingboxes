
import pygame
from scene import BouncingBoxesScene
import rgbcolors
import os.path
from random import randint
from math import sqrt
from animation import Explosion


def display_info():
    """ Print out information about the display driver and video information. """
    print('The display is using the "{}" driver.'.format(pygame.display.get_driver()))
    print('Video Info:')
    print(pygame.display.Info())  

def random_color():
    return pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255))

def random_coordinate_in_window(width, height, offset=100):
    return (randint(offset, width - offset), randint(offset, height - offset),)

def random_velocity():
    x = randint(1, 3)
    if randint(0, 1):
        x *= -1
    y = randint(1, 3)
    if randint(0, 1):
        y *= -1
    return (x, y)


class Box:
    width = 40
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, 'data')
    bounce_sound = os.path.join(data_dir, 'Monkey.aiff')
    reflect_sound = os.path.join(data_dir, 'Pillsbury.aif')
    def __init__(self, id, left, top, sound_on=True):
        self._id = id
        self._rect = pygame.Rect(left, top, Box.width, Box.width)
        self._color = random_color()
        # self._velocity = (1, 1)
        self._velocity = random_velocity()
        self._sound_on = sound_on
        self._bounce_count = randint(5, 10)
        self._is_alive = True
        if self._sound_on:
            try:
                self._bounce_sound = pygame.mixer.Sound(Box.bounce_sound)
            except pygame.error:
                print('Cannot open {}'.format(Box.bounce_sound))
                raise SystemExit(1)
            try:
                self._reflect_sound = pygame.mixer.Sound(Box.reflect_sound)
            except pygame.error:
                print('Cannot open {}'.format(Box.reflect_sound))
                raise SystemExit(1)

    def reflect(self, xmin, xmax, ymin, ymax):
        # print(self._rect.left, self._rect.top, xmin, xmax, ymin, ymax)
        if self._rect.midleft[0] <= xmin or self._rect.midright[0] >= xmax:
            self._velocity = (self._velocity[0] * -1, self._velocity[1])
        if self._rect.midtop[1] <= ymin or self._rect.midbottom[1] >= ymax:
            self._velocity = (self._velocity[0], self._velocity[1] * -1)
        if self._sound_on:
            self._reflect_sound.play()
        # self._velocity = tuple(map(lambda x: -x, self._velocity))

    def bounce(self):
        status = False
        if self._bounce_count > 0 and self._is_alive:
            if self._id != 0:
                self._bounce_count -= 1
            self._velocity = tuple(map(lambda x: -x, self._velocity))
            if self._sound_on:
                self._bounce_sound.play()
        else:
            self.stop()
            self._is_alive = False
            self._color = pygame.Color(rgbcolors.white)
            status = True
        return status

    @property
    def id(self):
        return self._id
    

    @property
    def rect(self):
        return self._rect

    @property
    def color(self):
        return self._color
    
    def distance_from(self, x, y):
        return sqrt((x - self._rect.centerx)**2 + (y - self._rect.centery)**2)

    def too_close(self, x, y, min_dist):
        return self.distance_from(x, y) < min_dist

    def stop(self):
        self._velocity = (0, 0)

    def set_velocity(self, x, y):
        self._velocity = (x, y)

    def update(self):
        self._rect.move_ip(self._velocity[0], self._velocity[1])

    def __repr__(self):
        return 'Box({}, {}, {})'.format(self._id, self._rect.left, self._rect.top) 

    def __str__(self):
        return '{} Box({}, {}): Color({}, {}, {}), width = {}, velocity = {}'.format(self._id, self._rect.left, self._rect.top, self._color.r, self._color.g, self._color.b, Box.width, self._velocity)

class BBDemo:
    def __init__(self):
        self._main_dir = os.path.split(os.path.abspath(__file__))[0]
        self._data_dir = os.path.join(self._main_dir, 'data')
        print("Our main directory is {}".format(self._main_dir))
        print("Our data directory is {}".format(self._data_dir))

    def run(self, sound_on=True):
        """This is the entry point to the game. It is the main function!"""
        if not pygame.font:
            print('Warning: fonts disabled.')
        if not pygame.mixer:
            print('Warning: sound disabled.')
        pygame.init()
        display_info()
        window_size = (800, 800)
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(window_size)
        background = pygame.Surface(window_size)
        title = 'Bouncing Boxes'
        pygame.display.set_caption(title)
        num_boxes = 10
        #boxes = [Box(i, randint(0,770), randint(0, 770), sound_on) for i in range(num_boxes)]

        # Let's make sure the boxes aren't on top of each other.
        coord = random_coordinate_in_window(*window_size)
        boxes = [Box(0, coord[0], coord[1], sound_on)]
        for i in range(1, num_boxes):
            coord = random_coordinate_in_window(*window_size)
            too_close = True
            while too_close:
                too_close = False
                for b in boxes:
                    too_close = too_close or b.too_close(*coord, 100)
                if too_close:
                    coord = random_coordinate_in_window(*window_size)
            boxes.append(Box(i, coord[0], coord[1], sound_on))

        boxes[0].set_velocity(10, 10)
        print(boxes)
        all = pygame.sprite.RenderUpdates()
        Explosion.containers = all

        current_scene = BouncingBoxesScene(boxes, screen, rgbcolors.navyblue, 60)
        current_scene.start()
        while current_scene.is_valid():
            clock.tick(current_scene.frame_rate())
            for event in pygame.event.get():
                current_scene.process_event(event)
            current_scene.update()            
            current_scene.draw()
            all.clear(screen, background)
            all.update()
            dirty = all.draw(screen)
            pygame.display.update()
        current_scene.end()
        print('Exiting!')
        pygame.quit()
        return 0
