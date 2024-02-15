import pygame


class RestartButton:
    def __init__(self, position, width, height, image_path, hover_color=(255, 255, 255), action=None):
        """
        Initialize the button with the given position, dimensions, image path, hover color, and optional action.

        Parameters:
        position (tuple): The position of the button (x, y).
        width (int): The width of the button.
        height (int): The height of the button.
        image_path (str): The file path to the button's image.
        hover_color (tuple, optional): The color of the button when hovered over. Defaults to (255, 255, 255).
        action (function, optional): The function to be executed when the button is clicked. Defaults to None.
        """
        self.base_image = pygame.image.load(image_path).convert_alpha()
        self.base_image = pygame.transform.scale(self.base_image, (width, height))
        self.hover_color = hover_color
        self.hover_image = self.base_image.copy()
        # Apply a tint to the hover image
        self.hover_image.fill(self.hover_color + (0,), None, pygame.BLEND_RGBA_ADD)
        self.image = self.base_image  # The current image to be drawn
        self.rect = self.base_image.get_rect(topleft=position)
        self.clicked = False
        self.hover = False
        self.visible = True
        self.action = action  # The callback action to be executed on click

    def draw(self, surface):
        """
        Draw the object on the given surface if it is visible.

        Parameters:
            surface: the surface to draw the object on
        """
        if self.visible:
            surface.blit(self.image, self.rect)

    def update(self):
        """
        Update the object based on its visibility and hover state.
        """
        if self.visible:
            if self.hover:
                self.image = self.hover_image
            else:
                self.image = self.base_image

    def handle_event(self, event):
        """
        Handle the given event, updating the button's hover and click states based on the event type and position.

        Args:
            event: The pygame event to handle.

        Returns:
            None
        """
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hover:  # Only consider it a click if the button is hovered
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.hover and self.clicked:
                self.clicked = False
                if self.action:
                    self.action()  # Execute the button's action callback

    def reset_state(self):
        """
        Reset the state of the object by setting clicked and hover flags to False and
        restoring the original image.
        """
        self.clicked = False
        self.hover = False
        self.image = self.base_image
