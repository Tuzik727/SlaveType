import pygame


class DifficultyButton:
    def __init__(self, x, y, width, height, text='', color=(12, 22, 24, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.clicked = False
        self.hover = False
        self.default_color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.font_color = (255, 255, 255)
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        # Change the button color based on hover state
        color = self.hover_color if self.hover else self.default_color
        pygame.draw.rect(screen, color, self.rect)
        text_surface = self.font.render(self.text, True, self.font_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        # Update the hover state based on mouse position
        self.hover = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.clicked = True
