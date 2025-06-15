import pygame
import os

class MenuButton(pygame.sprite.Sprite):
    """A clickable button in the main menu."""

    def __init__(
        self, x, y, callback, text="Play", play_color=(252, 186, 3),
        icon_idle=None, icon_hover=None, icon_click=None, font_size=48,
        hover_offset=None, icon_size=64
    ):
        super().__init__()
        base_path = os.path.dirname(__file__)  # path to src
        font_path = os.path.join(base_path, "fonts/Kenney_Future.ttf")

        if icon_idle is None:
            icon_idle = os.path.join(base_path, "tiles/menu/arrow_decorative_e_green.png")
        if icon_hover is None:
            icon_hover = os.path.join(base_path, "tiles/menu/arrow_decorative_e_yellow.png")
        if icon_click is None:
            icon_click = os.path.join(base_path, "tiles/menu/arrow_decorative_e_grey.png")

        # Load and scale the icons
        self.image_idle = pygame.transform.smoothscale(
            pygame.image.load(icon_idle).convert_alpha(), (icon_size, icon_size)
        )
        self.image_hover = pygame.transform.smoothscale(
            pygame.image.load(icon_hover).convert_alpha(), (icon_size, icon_size)
        )
        self.image_click = pygame.transform.smoothscale(
            pygame.image.load(icon_click).convert_alpha(), (icon_size, icon_size)
        )

        self.image = self.image_idle
        self.rect = self.image.get_rect(center=(x, y))

        self.callback = callback
        self.clicked = False
        self.hovered = False  # Track hover state

        # Font for button text
        self.font = pygame.font.Font(font_path, font_size)
        self.text = text
        self.text_color = play_color
        self.text_surface = self.font.render(self.text, True, self.text_color)

        self.hover_offset = hover_offset if hover_offset is not None else 120

    def update(self):
        """Update the button state based on mouse position and clicks.
        
        Checks if the button is hovered or clicked, and updates the image accordingly.
        """
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
            if mouse_pressed:
                self.image = self.image_click
                if not self.clicked:
                    self.clicked = True
                    self.callback()
            else:
                self.image = self.image_hover
                self.clicked = False
        else:
            self.image = self.image_idle
            self.clicked = False
            self.hovered = False

    def draw(self, surface):
        """Draw the button and its text on the given surface.
        
        Args:
            surface (pygame.Surface): The surface to draw the button on.

        """

        offset = self.hover_offset if self.hovered else 0  # změna zde
        arrow_pos = (self.rect.x + offset, self.rect.y)
        if self.hovered:
            # Draw text with shadow to the left of the arrow
            text_x = arrow_pos[0] - self.text_surface.get_width() - 10
            text_y = arrow_pos[1] + (self.image.get_height() - self.text_surface.get_height()) // 2
            # Shadow uses the actual button text
            shadow_surface = self.font.render(self.text, True, (40, 40, 40))
            surface.blit(shadow_surface, (text_x + 2, text_y + 2))
            surface.blit(self.text_surface, (text_x, text_y))
        surface.blit(self.image, arrow_pos)
        # If not hovered, draw arrow in original position (already handled by the image.blit call)
