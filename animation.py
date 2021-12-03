import pygame
import os.path

# Adapted aliens.py in pygame/examples
# https://github.com/pygame/pygame/blob/main/examples/aliens.py
class Explosion(pygame.sprite.Sprite):
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, 'data')
    image_path = os.path.join(data_dir, 'explosion1.gif')

    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        # super() leads to the wrong place?
        # super().__init__(self, self.containers)
        pygame.sprite.Sprite.__init__(self, self.containers)
        try:
            surface = pygame.image.load(Explosion.image_path)
        except pygame.error:
            raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
        img = surface.convert()
        if not Explosion.images:
            Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = Explosion.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life // Explosion.animcycle % 2]
        if self.life <= 0:
            self.kill()
