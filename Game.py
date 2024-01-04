import time
import random
import sys
import pygame

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
RESTART_BUTTON_SIZE = 70
FONT_SIZE = 25
TEXT_COLOR = (255, 255, 255)
STATISTICS_POSITIONS = [
    (int(SCREEN_HEIGHT * 0.75), "Time: {:.2f} seconds"),
    (int(SCREEN_HEIGHT * 0.82), "WPM: {:.2f}"),
    (int(SCREEN_HEIGHT * 0.86), "Accuracy: {:.2f}%")
]


def get_words(word_count=50):
    try:
        with open("text.txt") as file:
            all_lines = file.readlines()

            # Filter lines that have at least the specified word count
            valid_lines = [line.strip() for line in all_lines if len(line.split()) >= word_count]

            # If there are valid lines, select a random one
            if valid_lines:
                selected_line = random.choice(valid_lines)
                return selected_line
            else:
                print(f"No lines with at least {word_count} words found.")
                return None
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
        self.restart_img = pygame.transform.scale(pygame.image.load("restart.png"),
                                                  (RESTART_BUTTON_SIZE, RESTART_BUTTON_SIZE))
        self.input_text = ""
        self.active = True
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

    def display_text(self, title, y, font_size, text_color, underline=False, cursor_visible=False):
        font = pygame.font.Font("Fonts/Roboto-Medium.ttf", font_size)
        words = title.split()
        lines = []
        current_line = []

        for word in words:
            if get_text_width(' '.join(current_line + [word]), font_size) < SCREEN_WIDTH - 300:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]

        lines.append(' '.join(current_line))

        line_height = font.get_linesize()

        for i, line in enumerate(lines):
            text = font.render(line, True, text_color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + i * line_height))

            if underline and i == len(lines) - 1:
                pygame.draw.line(self.screen, text_color, (text_rect.left, text_rect.bottom),
                                 (text_rect.right, text_rect.bottom), 2)

            self.screen.blit(text, text_rect)

        pygame.display.update()

    def display_input_text(self, text, y, font_size, text_color, cursor_visible=False):
        font = pygame.font.Font("Fonts/Roboto-Medium.ttf", font_size)
        line_height = font.get_linesize()

        lines = text.split('\n')
        max_line_width = 0

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, text_color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y + i * line_height))
            self.screen.blit(text_surface, text_rect)

            # Update max_line_width if the current line is wider
            max_line_width = max(max_line_width, text_rect.width)

            if cursor_visible and i == len(lines) - 1:
                self.cursor_position = min(len(self.input_text), self.cursor_position)

                cursor_rect = pygame.Rect(
                    text_rect.left + get_text_width(line[:self.cursor_position], font_size),
                    text_rect.top,
                    1, text_rect.height)
                pygame.draw.rect(self.screen, "yellow", cursor_rect)

        pygame.display.update()

    def calculate_statistics(self):
        count = sum(1 for char_input, char_word in zip(self.input_text, self.words) if char_input == char_word)
        self.accuracy = (count * 100) / len(self.words)
        self.wpm = (len(self.input_text) * 60) / (5 * max(self.elapsed_time, 1))

    def display_time(self):
        time_rect = pygame.Rect(0, SCREEN_HEIGHT * 0.7, SCREEN_WIDTH, SCREEN_HEIGHT * 0.1)
        self.screen.fill((12, 22, 24, 255), time_rect)

        if self.end:
            time_text = "Time: {:.2f} seconds".format(self.final_time)
        else:
            if self.start_time and self.time_running:
                self.elapsed_time = round(time.time() - self.start_time, 2)
            time_text = "Time: {:.2f} seconds".format(self.elapsed_time)

        for position, template in STATISTICS_POSITIONS:
            if "Time" in template:
                font_size = int(SCREEN_HEIGHT / 40)
                self.display_text(time_text, position, font_size, TEXT_COLOR)

        pygame.display.update()

    def display_statistics(self):
        statistics_rect = pygame.Rect(0, SCREEN_HEIGHT * 0.7, SCREEN_WIDTH, SCREEN_HEIGHT * 0.2)
        self.screen.fill((12, 22, 24, 255), statistics_rect)
        for position, template in STATISTICS_POSITIONS:
            font_size = int(SCREEN_HEIGHT / 40)
            if "WPM" in template:
                self.display_text("WPM: {:.2f}".format(self.wpm), position, font_size, TEXT_COLOR)
            elif "Accuracy" in template:
                self.display_text("Accuracy: {:.2f}%".format(self.accuracy), position, font_size,
                                  TEXT_COLOR)

        pygame.display.update()

    def restart(self, words=50):
        self.end = False
        self.input_text = ""
        self.words = ""
        self.start_time = 0
        self.elapsed_time = 0
        self.wpm = 0

        while not self.words:
            self.words = get_words(words)

        self.screen.fill((12, 22, 24, 255))
        self.display_text("50", SCREEN_HEIGHT * 0.07, 20, "white")
        self.display_text("Slave Type", SCREEN_HEIGHT * 0.97, 20, "white")
        self.display_text(self.words, SCREEN_HEIGHT * 0.14, 20, "white", True)
        pygame.display.update()

    def handle_events(self):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not self.end:
                    if not self.time_running:  # Check if the timer is not already running
                        self.start_time = time.time()
                        self.time_running = True

                    self.calculate_statistics()
                    self.display_statistics()

                    if event.key == pygame.K_RETURN:
                        self.final_time = self.elapsed_time
                        self.time_running = False
                        self.end = True
                        restart_button_x = SCREEN_WIDTH // 2 - RESTART_BUTTON_SIZE // 2
                        restart_button_y = SCREEN_HEIGHT // 2 + 60
                        self.screen.blit(self.restart_img, (restart_button_x, restart_button_y))

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
            font_size = int(SCREEN_HEIGHT / 35)
            self.display_input_text(self.input_text, SCREEN_HEIGHT * 0.40, font_size, (250, 250, 250), cursor_visible=True)

            self.display_time()

            pygame.display.update()
            clock.tick(240)
        pygame.quit()
        sys.exit()
