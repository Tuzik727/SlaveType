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
    {"y": 0.84, "template": "WPM: {:.2f"},
    {"y": 0.88, "template": "Accuracy: {:.2f}%"}
]
STATISTICS_POSITIONS = [(int(SCREEN_HEIGHT * pos["y"]), pos["template"]) for pos in Positions]
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

        for word in words:
            # Check if adding the next word exceeds the line width
            if get_text_width(' '.join(current_line + [word]), font_size) < SCREEN_WIDTH - 300:
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
        time_rect = pygame.Rect(0, SCREEN_HEIGHT * 0.7, SCREEN_WIDTH, SCREEN_HEIGHT * 0.1)
        self.screen.fill((12, 22, 24, 255), time_rect)

        if self.end:
            time_text = "Time: {:.2f} seconds".format(self.final_time)
        else:
            if self.start_time and self.time_running:
                self.elapsed_time = round(time.time() - self.start_time, 2)
            time_text = "Time: {:.2f} seconds".format(self.elapsed_time)

        for y_pos, template in STATISTICS_POSITIONS:
            if "Time" in template:
                font_size = int(SCREEN_HEIGHT / 40)
                # Calculate the centered x position dynamically
                x_pos = SCREEN_WIDTH // 2
                # Pass the position as a tuple (x, y)
                self.render_text(time_text, (x_pos, y_pos), font_size, TEXT_COLOR)

    def display_statistics(self):
        statistics_rect = pygame.Rect(0, SCREEN_HEIGHT * 0.8, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen.fill((12, 22, 24, 255), statistics_rect)  # Fill with the background color

        for y_pos, template in STATISTICS_POSITIONS:
            font_size = int(SCREEN_HEIGHT / 50)
            x_pos = SCREEN_WIDTH // 2
            if "WPM" in template:
                stats_text = f"WPM: {self.wpm: .2f}"
            elif "Accuracy" in template:
                stats_text = f"Accuracy: {self.accuracy: .2f}%"
            else:
                continue

            # Render and blit the statistics text onto the statistics surface
            self.render_text(stats_text, (x_pos, y_pos), font_size, TEXT_COLOR)

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
        count = -1.5
        for button in self.difficultyButtons:
            button.rect.x = SCREEN_WIDTH // 2 + count * (button.rect.width + 10)
            button.rect.y = 10
            button.draw(self.screen)
            count += 1

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

        self.redraw_window()

    def handle_events(self):
        global SCREEN_WIDTH, SCREEN_HEIGHT, STATISTICS_POSITIONS
        for event in pygame.event.get():
            for button in self.difficultyButtons:
                button.handle_event(event)
                if button.clicked:
                    self.input_text = ""
                    button.clicked = False
                    self.restart(int(button.text))
            self.restart_button.handle_event(event)
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not self.end:
                    if not self.time_running:  # Check if the timer is not already running
                        self.start_time = time.time()
                        self.time_running = True

                    if event.key == pygame.K_RETURN:
                        self.final_time = self.elapsed_time
                        self.time_running = False
                        self.end = True

                    elif event.key == pygame.K_BACKSPACE:
                        if self.cursor_position > 0:
                            self.input_text = (
                                    self.input_text[: self.cursor_position - 1]
                                    + self.input_text[self.cursor_position:]
                            )
                            self.cursor_position -= 1
                    elif event.key == pygame.K_SPACE:
                        self.input_text = (
                                self.input_text[: self.cursor_position]
                                + " "
                                + self.input_text[self.cursor_position:]
                        )
                        self.cursor_position += 1
                    else:
                        self.input_text = (
                                self.input_text[: self.cursor_position]
                                + event.unicode
                                + self.input_text[self.cursor_position:]
                        )
                        self.cursor_position += 1

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                restart_button_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - RESTART_BUTTON_SIZE // 2,
                    SCREEN_HEIGHT // 2 + 60,
                    RESTART_BUTTON_SIZE,
                    RESTART_BUTTON_SIZE
                )
                if restart_button_rect.collidepoint(x, y):
                    self.restart()
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                # Recalculate STATISTICS_POSITIONS based on the new SCREEN_HEIGHT
                STATISTICS_POSITIONS = [(int(SCREEN_HEIGHT * pos["y"]), pos["template"]) for pos in
                                        Positions]
                # Redraw everything after resizing
                self.redraw_window()

    def run(self):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = self.screen.get_size()

        self.restart()
        self.running = True

        while self.running:
            clock = pygame.time.Clock()

            self.handle_events()
            # Dynamically adjust the position and size of the input text area
            input_text_rect = pygame.Rect(50, SCREEN_HEIGHT * 0.35, SCREEN_WIDTH - 100, SCREEN_HEIGHT * 0.1)

            pygame.draw.rect(self.screen, (12, 22, 24, 255), input_text_rect)
            current_font_size = self.get_scaled_font_size()
            text_position = self.get_relative_pos(0.5, 0.4)
            self.render_text(self.input_text, text_position, current_font_size, (0, 255, 0),
                             input_text=True, cursor_visible=True)

            self.display_time()
            self.calculate_statistics()
            self.display_statistics()

            if self.end:
                self.restart_button.draw(self.screen)

            if self.restart_button.clicked:
                self.restart_button.clicked = False
                self.restart()

            pygame.display.update()

            clock.tick(FPS)
        pygame.quit()
        sys.exit()
