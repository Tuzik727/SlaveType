import time
import sys
import pygame
import json
from src import DB
from src.DifficultyButtons import Button
from src.RestartButton import RestartButton

with open('db_config.json', 'r') as config_file:
    db_config = json.load(config_file)

with open("config.json") as config_file:
    config = json.load(config_file)

SCREEN_WIDTH = config["SCREEN_WIDTH"]
SCREEN_HEIGHT = config["SCREEN_HEIGHT"]
RESTART_BUTTON_SIZE = config["RESTART_BUTTON_SIZE"]
FONT_SIZE = config["FONT_SIZE"]
TEXT_COLOR = tuple(config["TEXT_COLOR"])
Positions = [
    {"y": 0.75, "template": "Time: {:.2f} seconds"},
    {"y": 0.84, "template": "WPM: {:.2f}"},
    {"y": 0.88, "template": "Accuracy: {:.2f}%"}
]
# Ensure that this list comprehension is used wherever STATISTICS_POSITIONS is defined or updated.
STATISTICS_POSITIONS = [(int(SCREEN_HEIGHT * pos["y"]), pos["template"]) for pos in Positions]
print(STATISTICS_POSITIONS)
FPS = config["FPS"]


def get_words(word_count):
    try:
        db = DB.Database(**db_config)
        random_sentence = db.get_random_sentence_by_word_count(word_count)
        db.close()
        return random_sentence
    except FileNotFoundError:
        print("Error: File 'text.txt' not found.")
        sys.exit()


def get_text_width(text, font_size=FONT_SIZE):
    font = pygame.font.Font("Fonts/Roboto-Bold.ttf", font_size)
    text_surface = font.render(text, True, TEXT_COLOR)
    return text_surface.get_width()


class SlaveType:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.restart_button = RestartButton(
            (SCREEN_WIDTH // 2 - RESTART_BUTTON_SIZE // 2, SCREEN_HEIGHT // 2 + 60),
            RESTART_BUTTON_SIZE,
            RESTART_BUTTON_SIZE,
            "Images/restart.png",
            (0, 100, 0)
        )
        button_width = 45
        button_height = 45
        button_spacing = 10  # Space between buttons
        num_buttons = 3
        total_buttons_width = num_buttons * button_width + (num_buttons - 1) * button_spacing
        buttons = [10, 20, 50]
        # Calculate the starting x position for the first button to center the group
        start_x = (SCREEN_WIDTH - total_buttons_width) // 2

        self.difficultyButtons = [
            Button(start_x + i * (button_width + button_spacing), 10, button_width, button_height, str(buttons[i])) for
            i in range(num_buttons)]
        self.input_text = ""
        self.end = False
        self.elapsed_time = 0
        self.start_time = 0
        self.words = ""
        self.accuracy = 0
        self.wpm = 0
        self.running = False
        self.time_running = False
        self.final_time = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_position = 0
        self.base_font_size = FONT_SIZE
        self.reference_resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.login_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, 100, 40, 'Login')
        self.focus_username = True  # Start with focus on the username field
        self.username_input = ""
        self.visible = True
        self.show_login_screen = True

    def get_scaled_font_size(self):
        current_height = self.screen.get_height()
        # Scale font size and convert to integer
        return int(self.base_font_size * (current_height / self.reference_resolution[1]))

    def get_relative_pos(self, x_percent, y_percent):
        # Calculate positions as percentages of the screen size
        current_width, current_height = self.screen.get_size()
        return int(current_width * x_percent), int(current_height * y_percent)

    def render_text(self, text, position, font_size, text_color, underline=False, cursor_visible=False,
                    input_text=False):
        font = pygame.font.Font("Fonts/Roboto-Medium.ttf", font_size)
        line_height = font.get_linesize()

        # Common logic for splitting text into lines
        words = text.split()
        lines = []
        current_line = []
        font_size = self.get_scaled_font_size()  # or use a smaller size if needed
        for word in words:
            max_line_width = self.screen.get_width() - 100
            if get_text_width(' '.join(current_line + [word]), font_size) < max_line_width:
                current_line.append(word)
            else:
                # If the line is full, append it to the lines list and start a new line
                lines.append(' '.join(current_line))
                current_line = [word]

        # Add the last line to the lines list
        lines.append(' '.join(current_line))

        # Rendering logic
        x_pos, y_pos = position
        y_pos_offset = 0

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, text_color)
            text_rect = text_surface.get_rect(center=(x_pos, y_pos + y_pos_offset))
            self.screen.blit(text_surface, text_rect)

            y_pos_offset += line_height  # Increase the y position offset for the next line

            if input_text and cursor_visible and i == len(lines) - 1:
                # Set the cursor width to a fixed value for a thin line cursor
                cursor_width = 2  # or whatever width you prefer for your cursor
                cursor_height = font.get_height()

                # Get the current time in milliseconds
                time_ms = pygame.time.get_ticks()
                if (time_ms // 500) % 2 == 0:
                    cursor_x_offset = 0
                    # Render each character up to the cursor position to get the exact cursor position
                    for char in self.input_text[:self.cursor_position]:
                        char_width, _ = font.size(char)
                        cursor_x_offset += char_width

                    # Calculate the cursor's x position
                    cursor_x = text_rect.left + cursor_x_offset
                    cursor_y = text_rect.top

                    # Draw the cursor as a solid box
                    cursor_rect = pygame.Rect(cursor_x, cursor_y, cursor_width, cursor_height)
                    pygame.draw.rect(self.screen, (255, 255, 255), cursor_rect)
            # Draw the underline if this is not the input text
            if not input_text and underline and i == len(lines) - 1:
                pygame.draw.line(self.screen, (255, 255, 255), (text_rect.left, text_rect.bottom),
                                 (text_rect.right, text_rect.bottom), 2)

    def calculate_statistics(self):
        # Calculate the number of correct characters typed
        correct_chars = sum(1 for char_input, char_word in zip(self.input_text, self.words) if char_input == char_word)
        total_chars = len(self.words)

        # Update accuracy
        self.accuracy = (correct_chars / total_chars) * 100 if total_chars > 0 else 0

        # Update WPM (Words Per Minute)
        self.wpm = (len(self.input_text) / 5) / (self.elapsed_time / 60) if self.elapsed_time > 0 else 0

    def display_time(self):
        current_width, current_height = self.screen.get_size()  # Get the current window size
        time_rect = pygame.Rect(0, current_height * 0.7, current_width, current_height * 0.1)
        self.screen.fill((12, 22, 24, 255), time_rect)

        if self.end:
            time_text = "Time: {:.2f} seconds".format(self.final_time)
        else:
            if self.start_time and self.time_running:
                self.elapsed_time = round(time.time() - self.start_time, 2)
            time_text = "Time: {:.2f} seconds".format(self.elapsed_time)

        for y_pos, template in STATISTICS_POSITIONS:
            font_size = self.get_scaled_font_size() // 2
            # Calculate the centered x position dynamically
            x_pos = current_width // 2
            # Pass the position as a tuple (x, y)
            self.render_text(time_text, (x_pos, y_pos), font_size, TEXT_COLOR)

    def display_statistics(self):
        current_width, current_height = self.screen.get_size()  # Get the current window size
        statistics_rect = pygame.Rect(0, current_height * 0.8, current_width, current_height)
        self.screen.fill((12, 22, 24, 255), statistics_rect)  # Fill with the background color

        for y_pos, template in STATISTICS_POSITIONS:
            font_size = self.get_scaled_font_size() // 2
            x_pos = self.screen.get_width() // 2
            if "WPM" in template:
                stats_text = f"WPM: {self.wpm:.2f}"
            elif "Accuracy" in template:
                stats_text = f"Accuracy: {self.accuracy:.2f}%"
            else:
                continue

            # Render and blit the statistics text onto the statistics surface
            self.render_text(stats_text, (x_pos, y_pos), font_size, TEXT_COLOR)

    def draw_login_screen(self):
        current_width, current_height = self.screen.get_size()
        self.screen.fill((12, 22, 24, 255))

        # Dynamically calculate positions
        username_pos = (current_width // 2, current_height // 2 - 50)
        self.login_button.rect.center = (current_width // 2, current_height // 2 + 50)

        # Draw username field and login button
        self.render_text("Username: " + self.username_input, username_pos, self.get_scaled_font_size(), TEXT_COLOR)
        if self.show_login_screen:
            self.login_button.draw(self.screen)

    def redraw_window(self):
        # Clear the entire screen
        self.screen.fill((12, 22, 24, 255))
        # Redraw the input text
        current_font_size = self.get_scaled_font_size()
        text_position = self.get_relative_pos(0.5, 0.4)
        self.render_text(self.input_text, text_position, current_font_size, (0, 255, 0),
                         input_text=True, cursor_visible=True)
        # Redraw words
        words_position = self.get_relative_pos(0.5, 0.14)
        self.render_text(self.words, words_position, current_font_size, (0, 153, 51), underline=True)
        # Update and redraw the restart button position
        self.restart_button.rect.x = SCREEN_WIDTH // 2 - RESTART_BUTTON_SIZE // 2
        self.restart_button.rect.y = SCREEN_HEIGHT // 2 + 60  # Adjust y-coordinate as needed
        if self.end:
            self.restart_button.draw(self.screen)
        # Recalculate and redraw the statistics
        [(int(SCREEN_HEIGHT * pos["y"]), pos["template"]) for pos in
         Positions]
        # Redraw the time
        self.display_time()
        self.display_statistics()
        # Redraw buttons
        start_x = self.get_button_positions()
        for i, button in enumerate(self.difficultyButtons):
            button.rect.x = start_x + i * (button.rect.width + 10)
            button.rect.y = 10  # Keep the y-coordinate constant or adjust as needed
            button.draw(self.screen)

    def restart(self, words=50):
        self.end = False
        self.input_text = ""
        self.words = ""
        self.start_time = 0
        self.elapsed_time = 0
        self.wpm = 0
        self.accuracy = 0  # Reset accuracy
        self.final_time = 0  # Reset the final time

        while not self.words:
            self.words = get_words(words)
        else:
            self.words = self.words
        self.redraw_window()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.show_login_screen:
                    self.handle_login_events()
                    self.handle_login_keydown_event(event)
                else:
                    self.handle_keydown_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousedown_event(event)
            elif event.type == pygame.VIDEORESIZE:
                self.handle_video_resize_event(event.size)

    def handle_login_keydown_event(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.username_input = self.username_input[:-1]
        else:
            # Only add characters if they are printable
            if event.unicode.isprintable():
                self.username_input += event.unicode
        # Redraw the login screen to reflect the updated username_input
        self.draw_login_screen()

    def handle_keydown_event(self, event):
        if not self.end:
            if not self.time_running:  # Start the timer when the first key is pressed
                self.start_time = time.time()
                self.time_running = True

            if event.key == pygame.K_RETURN:
                self.finalize_input()
            elif event.key == pygame.K_BACKSPACE:
                self.remove_character_at_cursor()
            else:
                self.add_character_at_cursor(event.unicode)

    def handle_mousedown_event(self, event):
        x, y = event.pos
        if self.show_login_screen:
            # Assuming that the login_button has the 'handle_event' method which sets 'clicked' to True
            self.login_button.handle_event(event)
            if self.login_button.clicked:
                self.on_login_button_click()
        elif self.restart_button.rect.collidepoint(x, y) and self.end:
            self.restart()
        else:
            for button in self.difficultyButtons:
                button.handle_event(event)
                if button.clicked:
                    self.change_difficulty(button)

    def handle_video_resize_event(self, size):
        width, height = size
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.update_positions_based_on_size(width, height)
        self.redraw_window()

    def change_difficulty(self, button):
        self.input_text = ""
        button.clicked = False
        self.restart(int(button.text))

    def finalize_input(self):
        self.final_time = self.elapsed_time
        self.time_running = False
        self.end = True

    def remove_character_at_cursor(self):
        if self.cursor_position > 0:
            self.input_text = (
                    self.input_text[: self.cursor_position - 1]
                    + self.input_text[self.cursor_position:]
            )
            self.cursor_position -= 1

    def add_character_at_cursor(self, char):
        if char == ' ':
            self.input_text += ' '
        else:
            self.input_text += char
        self.cursor_position += 1

    def update_positions_based_on_size(self, screen_width, screen_height):
        global STATISTICS_POSITIONS
        STATISTICS_POSITIONS = [
            (int(screen_height * pos["y"]), pos["template"]) for pos in Positions
        ]

    def get_button_positions(self):
        button_width = 45
        button_height = 45
        button_spacing = 10  # Space between buttons
        num_buttons = 3
        total_buttons_width = num_buttons * button_width + (num_buttons - 1) * button_spacing
        start_x = (self.screen.get_width() - total_buttons_width) // 2
        return start_x

    def handle_login_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.login_button.update(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.login_button.rect.collidepoint(mouse_pos):
                    self.on_login_button_click()

    def on_login_button_click(self):
        print("Login button clicked!")
        self.login_button.visible = False  # Set the button to be invisible
        self.show_login_screen = False

    def dynamic_run_events(self):
        width, height = self.screen.get_size()
        # Dynamically adjust the position and size of the input text area
        input_text_rect = pygame.Rect(50, height * 0.35, width - 100, height * 0.1)

        pygame.draw.rect(self.screen, (12, 22, 24, 255), input_text_rect)
        current_font_size = self.get_scaled_font_size()
        text_position = self.get_relative_pos(0.5, 0.4)
        self.render_text(self.input_text, text_position, current_font_size, (0, 255, 0),
                         input_text=True, cursor_visible=True)

        words_position = self.get_relative_pos(0.5, 0.14)
        self.render_text(self.words, words_position, self.get_scaled_font_size(), (0, 153, 51), underline=True)

        self.display_time()
        self.calculate_statistics()
        self.display_statistics()

        if self.end:
            self.restart_button.draw(self.screen)

        if self.restart_button.clicked:
            self.restart_button.clicked = False
            self.restart()

    def run(self):
        self.restart()
        self.running = True
        clock = pygame.time.Clock()

        while self.running:
            if self.show_login_screen:
                self.handle_events()
                self.draw_login_screen()
            else:
                self.dynamic_run_events()
                self.handle_events()

            pygame.display.update()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()
