import pygame


class TextButton:
    def __init__(self, position, width, height, text, font_path, font_size, text_color, background_color,
                 hover_background_color, is_leaderboard_button=False):
        """
        Initialize the button with the given parameters.

        Parameters:
            position (tuple): The position of the button.
            width (int): The width of the button.
            height (int): The height of the button.
            text (str): The text displayed on the button.
            font_path (str): The path to the font file.
            font_size (int): The size of the font.
            text_color (tuple): The color of the text.
            background_color (tuple): The background color of the button.
            hover_background_color (tuple): The background color of the button when hovered over.
            is_leaderboard_button (bool, optional): Whether the button is a leaderboard button. Defaults to False.
        """
        self.is_leaderboard_button = is_leaderboard_button
        self.clicked = False
        self.position = position
        self.width = width
        self.height = height
        self.text = text
        self.font = pygame.font.Font(font_path, font_size)
        self.text_color = text_color
        self.background_color = background_color
        self.hover_background_color = hover_background_color
        self.hover = False
        self.rect = pygame.Rect(position, (width, height))

    def draw(self, screen):
        """
        Draw the button with the appropriate background color and render the text.
        """
        # Draw the button with the appropriate background color
        current_color = self.hover_background_color if self.hover else self.background_color
        pygame.draw.rect(screen, current_color, self.rect)

        # Render the text
        text_surface = self.font.render(self.text, True, self.text_color)
        # Center the text inside the button
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Blit the text onto the screen
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """
        Handle the given event for the object.

        Parameters:
            event (Event): The event to be handled.

        Returns:
            None
        """
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) and self.clicked:
                # Button click is released, perform an action
                if not self.is_leaderboard_button:
                    self.clicked = False
