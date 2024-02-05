import pygame


class RestartButton:
    def __init__(self, position, width, height, image_path, hover_color):
        self.base_image = pygame.image.load(image_path).convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (width, height))
        self.hover_color = hover_color
        self.image = self.base_image.copy()  # Make a copy for modifications
        self.rect = self.base_image.get_rect(topleft=position)
        self.clicked = False
        self.hover = False  # Indicates if the button is being hovered over

    def draw(self, surface):
        if self.hover:
            # Apply a tint to the image to indicate a hover
            filled_hover_image = self.base_image.copy()
            filled_hover_image.fill(self.hover_color + (0,), None, pygame.BLEND_RGBA_ADD)
            self.image = filled_hover_image
        else:
            self.image = self.base_image

        # Draw the current image of the button
        surface.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check if the mouse is over the button and set hover state
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) and self.clicked:
                self.clicked = False
                # Perform action here if button is clicked
