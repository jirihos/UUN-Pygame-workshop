import pygame

class MenuButton(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, callback):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((200, 30, 30))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.callback = callback
    
    def update(self):
        left_mouse_btn = pygame.mouse.get_pressed()[0]
        if left_mouse_btn and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.callback()