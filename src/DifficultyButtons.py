import pygame


class Button:
    def __init__(self, x, y, width, height, text='', color=(12, 22, 24, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.clicked = False

    def draw(self, screen):
        # Draw button
        pygame.draw.rect(screen, self.color, self.rect)
        # Draw button text
        font = pygame.font.Font(None, 35)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
