import time
import sys
import pygame
import json
from src import DB
from src.utils.DifficultyButtons import DifficultyButton
from src.utils.RestartButton import RestartButton
from src.utils.TextButton import TextButton

with open('../config/db_config.json', 'r') as config_file:
    db_config = json.load(config_file)

with open("../config/config.json") as config_file:
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


def get_text_width(text, font_size=FONT_SIZE):
    """
    Calculates the width of the given text when rendered with the specified font size.

    Args:
        text (str): The text to calculate the width for.
        font_size (int, optional): The font size to use for rendering the text. Defaults to FONT_SIZE.

    Returns:
        int: The width of the rendered text in pixels.
    """
    font = pygame.font.Font("../assets/fonts/Roboto-Bold.ttf", font_size)
    text_surface = font.render(text, True, TEXT_COLOR)
    return text_surface.get_width()


def update_positions_based_on_size(screen_width, screen_height):
    """
    Update the positions based on the screen width and height.

    Args:
        screen_width (int): The width of the screen.
        screen_height (int): The height of the screen.

    Returns:
        None
    """
    global STATISTICS_POSITIONS
    STATISTICS_POSITIONS = [
        (int(screen_height * pos["y"]), pos["template"]) for pos in Positions
    ]


class SlaveType:
    def __init__(self):
        """
        Constructor for initializing various attributes and objects.
        """
        self.already_one_time_clicked = False
        self.show_signup_screen = None
        self.db = DB.Database(**db_config)
        self.game_id = 0
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.restart_button = RestartButton(
            (SCREEN_WIDTH // 2 - RESTART_BUTTON_SIZE // 2, SCREEN_HEIGHT // 2 + 60),
            RESTART_BUTTON_SIZE,
            RESTART_BUTTON_SIZE,
            "../assets/images/restart.png",
            (0, 100, 0)
        )
        self.back_button = TextButton(position=(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT * 0.8),
                                      width=120,
                                      height=40,
                                      text="Back",
                                      font_path="../assets/fonts/Roboto-Bold.ttf",
                                      font_size=25,
                                      text_color=(255, 255, 255),
                                      background_color=(12, 22, 24, 255),
                                      hover_background_color=(150, 150, 150))
        self.leaderboard_button = TextButton(position=(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT * 0.065),
                                             width=120,
                                             height=40,
                                             text="Leaderboard",
                                             font_path="../assets/fonts/Roboto-Bold.ttf",
                                             font_size=20,
                                             text_color=(255, 255, 255),
                                             background_color=(12, 22, 24, 255),
                                             hover_background_color=(150, 150, 150),
                                             is_leaderboard_button=True)
        self.leaderboard_button.visible = True
        self.difficulty_button_10 = TextButton(position=(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT * 0.01), width=50,
                                               height=40, text="10", font_path="../assets/fonts/Roboto-Bold.ttf", font_size=30,
                                               text_color=(255, 255, 255),
                                               background_color=(12, 22, 24, 255),
                                               hover_background_color=(150, 150, 150))
        self.difficulty_button_10.visible = True
        self.difficulty_button_20 = TextButton(position=(SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT * 0.01), width=50,
                                               height=40, text="20", font_path="../assets/fonts/Roboto-Bold.ttf", font_size=30,
                                               text_color=(255, 255, 255),
                                               background_color=(12, 22, 24, 255),
                                               hover_background_color=(150, 150, 150))
        self.difficulty_button_50 = TextButton(position=(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT * 0.01), width=50,
                                               height=40, text="50", font_path="../assets/fonts/Roboto-Bold.ttf", font_size=30,
                                               text_color=(255, 255, 255),
                                               background_color=(12, 22, 24, 255),
                                               hover_background_color=(150, 150, 150))
        self.difficulty_buttons = [self.difficulty_button_10, self.difficulty_button_20, self.difficulty_button_50]
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
        self.login_button = DifficultyButton(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 5.5, 50, 'Login')
        self.signup_button = DifficultyButton(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 5.5, 50,
                                              'Sign Up')
        self.focus_username = True  # Start with focus on the username field
        self.username_input = ""
        self.visible = True
        self.show_login_screen = True
        self.password = ""

    def get_words(self, word_count):
        """
        Get a random sentence from the database based on the specified word count.

        Parameters:
            word_count (int): The number of words in the random sentence to retrieve

        Returns:
            str: A random sentence from the database
        """
        try:
            random_sentence = self.db.get_random_sentence_by_word_count(word_count)
            return random_sentence
        except FileNotFoundError:
            print("Error: File 'text.txt' not found.")
            sys.exit()

    def get_scaled_font_size(self):
        """
        Calculate and return the scaled font size based on the current screen height.
        """
        current_height = self.screen.get_height()
        # Scale font size and convert to integer
        return int(self.base_font_size * (current_height / self.reference_resolution[1]))

    def get_relative_pos(self, x_percent, y_percent):
        """
        Calculate positions as percentages of the screen size

        Parameters:
            x_percent (float): The x-coordinate percentage
            y_percent (float): The y-coordinate percentage

        Returns:
            tuple: A tuple containing the x and y coordinates as integers
        """
        # Calculate positions as percentages of the screen size
        current_width, current_height = self.screen.get_size()
        return int(current_width * x_percent), int(current_height * y_percent)

    def render_text(self, text, position, font_size, text_color, underline=False, cursor_visible=False,
                    input_text=False):
        """
        Render the given text on the screen at the specified position with the specified font size and color.

        Parameters:
        - text: The text to be rendered
        - position: The (x, y) position where the text should be rendered
        - font_size: The size of the font to be used for rendering the text
        - text_color: The color of the rendered text
        - underline: (Optional) Whether to underline the text
        - cursor_visible: (Optional) Whether the cursor is visible for input text
        - input_text: (Optional) Whether the text is input text

        Returns:
        None
        """
        font = pygame.font.Font("../assets/fonts/Roboto-Medium.ttf", font_size)
        line_height = font.get_linesize()

        # Common logic for splitting text into lines
        words = text.split()
        lines = []
        current_line = []
        font_size = self.get_scaled_font_size()  # or use a smaller size if needed
        for word in words:
            max_line_width = self.screen.get_width() - 200
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

                    if get_text_width(line, font_size) > 720:
                        # Split the line by spaces to get words
                        words = line.split(' ')
                        while words and get_text_width(' '.join(words), font_size) > SCREEN_WIDTH - 200:
                            words.pop()
                        # Join the words back into a line
                        line = ' '.join(words)
                        # Update the self.input_text with the new line without the last word
                        self.input_text = self.input_text[:self.input_text.rfind(line)]
            # Draw the underline if this is not the input text
            if not input_text and underline and i == len(lines) - 1:
                pygame.draw.line(self.screen, (255, 255, 255), (text_rect.left, text_rect.bottom),
                                 (text_rect.right, text_rect.bottom), 2)

    def calculate_statistics(self):
        """
        Calculate the number of correct characters typed, update accuracy, and update WPM.
        """
        # Calculate the number of correct characters typed
        correct_chars = sum(1 for char_input, char_word in zip(self.input_text, self.words) if char_input == char_word)
        total_chars = len(self.words)

        # Update accuracy
        self.accuracy = (correct_chars / total_chars) * 100 if total_chars > 0 else 0

        # Update WPM (Words Per Minute)
        self.wpm = (len(self.input_text) / 5) / (self.elapsed_time / 60) if self.elapsed_time > 0 else 0

    def display_time(self):
        """
        Display the current time on the screen and update it dynamically.
        """
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
        """
        Display statistics on the screen using the current window size and specific text templates.
        """
        current_width, current_height = self.screen.get_size()  # Get the current window size
        statistics_rect = pygame.Rect(0, current_height * 0.8, current_width, current_height)
        self.screen.fill((12, 22, 24, 255), statistics_rect)  # Fill with the background color

        for y_pos, template in STATISTICS_POSITIONS:
            font_size = self.get_scaled_font_size() // 2
            x_pos = self.screen.get_width() // 2
            if "WPM" in template:
                stats_text = f"WPM: {self.wpm: .2f}"
            elif "Accuracy" in template:
                stats_text = f"Accuracy: {self.accuracy: .2f}%"
            else:
                continue

            # Render and blit the statistics text onto the statistics surface
            self.render_text(stats_text, (x_pos, y_pos), font_size, TEXT_COLOR)

    def restart(self, words=50):
        """
        Restart the typing test with the specified number of words.

        Args:
            words (int): The number of words for the typing test.

        Returns:
            None
        """
        self.end = False
        self.input_text = ""
        self.words = ""
        self.start_time = 0
        self.elapsed_time = 0
        self.wpm = 0
        self.accuracy = 0  # Reset accuracy
        self.final_time = 0  # Reset the final time

        while not self.words:
            self.words = self.get_words(words)
        else:
            self.words = self.words

    def handle_events(self):
        """
        Handle events such as mouse position, button updates, and various pygame events.
        """
        mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position
        if self.show_login_screen:
            self.login_button.update(mouse_pos)
            self.signup_button.update(mouse_pos)
        for event in pygame.event.get():
            self.leaderboard_button.handle_event(event)
            self.back_button.handle_event(event)
            self.handle_difficulty_event(event)

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
            elif event.type == pygame.MOUSEMOTION:
                self.restart_button.handle_event(event)
                self.restart_button.hover = self.restart_button.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousedown_event(event)
            elif event.type == pygame.VIDEORESIZE:
                self.handle_video_resize_event(event.size)

    def handle_difficulty_event(self, event):
        """
        Handle the difficulty event by iterating through the difficulty buttons, handling the event for each button,
         and restarting the game with the selected difficulty if a button is clicked.

        Parameters:
        - event: The event to be handled.

        Return:
        - None
        """
        for button in self.difficulty_buttons:
            button.handle_event(event)
            if button.clicked:
                self.restart(words=int(button.text))

    def handle_keydown_event(self, event):
        """
        Handle the keydown event, perform corresponding actions based on the key pressed.

        Args:
            event: The keydown event object containing information about the key pressed.

        Returns:
            None
        """
        if not self.end:
            if not self.time_running:  # Start the timer when the first key is pressed
                self.start_time = time.time()
                self.time_running = True

            if event.key == pygame.K_RETURN:
                self.restart_button.visible = True
                self.final_time = self.elapsed_time
                self.save_user_statistics()
                self.time_running = False
                self.end = True
                self.game_id += 1
            elif event.key == pygame.K_BACKSPACE:
                self.remove_character_at_cursor()
            elif event.key == pygame.K_LCTRL:
                self.restart()
            else:
                self.add_character_at_cursor(event.unicode)

    def handle_mousedown_event(self, event):
        """
        Handle the mousedown event, checking for login and signup button clicks, and restart button clicks.
        Parameters:
            event: The event object containing the position of the mouse click.
        Returns:
            None
        """
        x, y = event.pos
        if self.show_login_screen:
            self.login_button.handle_event(event)
            self.signup_button.handle_event(event)

            if self.login_button.clicked:
                self.user_login(self.username_input, self.password)

            elif self.signup_button.clicked:
                if self.already_one_time_clicked:
                    self.user_signup(self.username_input, self.password)
                else:
                    self.already_one_time_clicked = True
                    self.show_signup_screen = True
        elif self.restart_button.rect.collidepoint(x, y):
            self.restart_button.visible = False
            self.restart()

    def handle_video_resize_event(self, size):
        """
        Handle the video resize event by updating the screen size, positions of various buttons, and redrawing
         the entire screen with the updated positions.

        Parameters:
        - self: the object instance
        - size: a tuple containing the new width and height of the screen

        Returns:
        - None
        """
        width, height = size
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Update positions based on the new size
        update_positions_based_on_size(width, height)

        # Update the restart button's position
        self.restart_button.rect.center = (width // 2, height // 2 + 60)

        # Update the leaderboard button's position
        self.leaderboard_button.position = (width // 2, height * 0.09)
        self.leaderboard_button.rect.center = self.leaderboard_button.position

        count = -100
        for button in self.difficulty_buttons:
            button.position = (width // 2 + count, height * 0.04)
            button.rect.center = button.position
            count += 100
        # Redraw the entire screen with the updated positions
        self.screen.fill((12, 22, 24, 255))
        self.dynamic_run_events()
        pygame.display.update()

    def remove_character_at_cursor(self):
        """
        Remove the character at the cursor position in the input text.
        """
        if self.cursor_position > 0:
            self.input_text = (
                    self.input_text[: self.cursor_position - 1]
                    + self.input_text[self.cursor_position:]
            )
            self.cursor_position -= 1

    def add_character_at_cursor(self, char):
        """
        Adds a character at the current cursor position.

        Parameters:
        char (str): The character to be added at the cursor position.

        Returns:
        None
        """
        if char == ' ':
            self.input_text += ' '
        else:
            self.input_text += char
        self.cursor_position += 1

    def handle_login_events(self):
        """
        Handle login events such as mouse movements and button clicks.
        """
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEMOTION:
                self.login_button.update(mouse_pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.login_button.rect.collidepoint(mouse_pos):
                    self.login_button.visible = False
                    self.show_login_screen = False

    def user_login(self, username, password):
        """
        Function for user login with username and password parameters.
        """
        massage = ""
        if self.db.verify_user_credentials(username, password):
            massage = "Login successful!"
            self.show_login_screen = False
        else:
            massage = "Login failed! Incorrect username or password."

        message_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150)
        self.render_text(massage, message_position, self.get_scaled_font_size(), (255, 255, 255))
        pygame.display.update()
        pygame.time.delay(2000)

    def handle_login_keydown_event(self, event):
        """
        Handle the keydown event for login input fields.

        Args:
            event: The pygame event object containing information about the key press.

        Returns:
            None
        """
        if event.key == pygame.K_BACKSPACE:
            if self.focus_username and self.username_input:
                self.username_input = self.username_input[:-1]
                self.cursor_position = max(0, self.cursor_position - 1)
            elif self.password:
                self.password = self.password[:-1]
                self.cursor_position = max(0, self.cursor_position - 1)
            else:
                self.password = self.password[:-1]
        elif event.key == pygame.K_TAB:
            self.focus_username = not self.focus_username  # Toggle focus between username and password
        elif event.key == pygame.K_RETURN:
            self.user_login(self.username_input, self.password)
        else:
            # Only add characters if they are printable
            if event.unicode.isprintable():
                if self.focus_username:
                    self.username_input += event.unicode
                else:
                    self.password += event.unicode

    def draw_login_screen(self):
        """
        Draw the login screen with input fields and buttons centered on the screen.
        """
        current_width, current_height = self.screen.get_size()
        self.screen.fill((12, 22, 24, 255))

        # Calculate positions
        form_height = 200  # The total height of the login form
        start_y = (current_height - form_height) // 2  # Vertical centering

        font_size = self.get_scaled_font_size()
        username_pos = (current_width // 2, start_y)
        password_pos = (current_width // 2, start_y + 100)
        login_button_pos = (current_width // 2 * 0.9, start_y * 1.8)
        signup_button_pos = (current_width // 2 * 1.12, start_y * 1.8)

        # Update button positions
        self.login_button.rect.center = login_button_pos
        self.signup_button.rect.center = signup_button_pos

        # Render input fields with underlines
        self.render_text("Username: " + self.username_input, username_pos, font_size, TEXT_COLOR, underline=True)
        self.render_text("Password: " + ('*' * len(self.password)), password_pos, font_size, TEXT_COLOR, underline=True)

        # Draw buttons
        self.login_button.draw(self.screen)
        self.signup_button.draw(self.screen)

    def dynamic_run_events(self):
        """
        This function handles the dynamic running of events. It sets the input text rectangle, renders text,
         sets the position of words, draws buttons, displays time, calculates statistics, and displays statistics.
        """
        width, height = self.screen.get_size()
        input_text_rect = pygame.Rect(50, height * 0.35, width - 100, height * 0.1)
        pygame.draw.rect(self.screen, (12, 22, 24, 255), input_text_rect)

        self.render_text(self.input_text, self.get_relative_pos(0.5, 0.4), self.get_scaled_font_size(), (0, 255, 0),
                         input_text=True, cursor_visible=True)

        words_position = self.get_relative_pos(0.5, 0.14)
        self.render_text(self.words, words_position, self.get_scaled_font_size(), (0, 153, 51), underline=True)
        self.difficulty_button_10.draw(self.screen)
        self.difficulty_button_20.draw(self.screen)
        self.difficulty_button_50.draw(self.screen)
        self.leaderboard_button.draw(self.screen)
        self.display_time()
        self.calculate_statistics()
        self.display_statistics()

    def user_signup(self, username_input, password):
        """
        This function handles user signup by inserting the username and password into the database.
        It takes the username_input and password as parameters and does not return anything.
        """
        massage = ""
        if self.db.insert_user(username_input, password):
            massage = "Signup successful!"
        else:
            massage = "Signup failed! Username already exists."

        message_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150)
        self.render_text(massage, message_position, self.get_scaled_font_size(), (255, 255, 255))
        pygame.display.update()
        pygame.time.delay(2000)

    def save_user_statistics(self):
        """
        Save user statistics to the database.
        """
        self.db.insert_user_statistics(self.db.get_user_id_by_username(self.username_input), self.game_id,
                                       self.wpm, self.accuracy, self.elapsed_time)

    def show_leaderboard(self):
        """
        Function to display the leaderboard on the screen, including best daily scores and best scores of all time.
        This function fetches the top daily scores and all-time scores from the database and renders them on the screen.
        """
        self.screen.fill((12, 22, 24, 255))  # Clean the screen
        screen_width, screen_height = self.screen.get_size()

        daily_scores = self.db.get_top_daily_scores(limit=5)
        all_time_scores = self.db.get_top_scores(limit=5)

        font_size = self.get_scaled_font_size() - 5
        start_y = screen_height * 0.1  # Starting y position to draw the leaderboard
        column_spacing = screen_width // 4  # Spacing between the two columns

        # Render the leaderboard titles
        self.render_text("Best Daily Scores", (column_spacing, start_y - font_size), font_size, (255, 255, 255))
        self.render_text("Best Scores of All Time", (screen_width - column_spacing, start_y - font_size), font_size,
                         (255, 255, 255))

        # Render the column headers
        daily_headers = "Rank  Username  WPM  Accuracy"
        all_time_headers = "Rank  Username  WPM  Accuracy"
        self.render_text(daily_headers, (column_spacing, start_y + font_size), font_size, (255, 255, 255))
        self.render_text(all_time_headers, (screen_width - column_spacing, start_y + font_size), font_size,
                         (255, 255, 255))

        # Define a padding value to control the space between lines
        padding = screen_height * 0.05

        # Render the daily scores
        for i, score in enumerate(daily_scores):
            rank = i + 1
            username, wpm, accuracy, date_played = score
            score_text = f"{rank}  {username}  {wpm: .2f}  {accuracy: .2f}%"
            line_height = font_size + padding  # Calculate the total height for each line including padding
            self.render_text(score_text, (column_spacing, start_y + line_height * (3 + i)), font_size, (255, 255, 255))

        # Render the all-time best scores
        for i, score in enumerate(all_time_scores):
            rank = i + 1
            username, wpm, accuracy, date_played = score
            score_text = f"{rank}  {username}  {wpm: .2f}  {accuracy: .2f}%"
            line_height = font_size + padding  # Calculate the total height for each line including padding
            self.render_text(score_text, (screen_width - column_spacing, start_y + line_height * (3 + i)), font_size,
                             (255, 255, 255))

        self.back_button.rect.center = (screen_width // 2, screen_height - self.back_button.rect.height // 2)
        self.back_button.draw(self.screen)
        pygame.display.update()

    def run(self):
        """
        The run function restarts, sets the running flag to True, and then runs a game loop until the running flag
        is set to False. It handles events, updates the screen, and manages the clock to control the frame rate.
        Finally, it quits pygame and exits the program.
        """
        self.restart()
        self.running = True
        clock = pygame.time.Clock()

        while self.running:
            self.screen.fill((12, 22, 24, 255))
            self.handle_events()
            self.dynamic_run_events()
            if not self.show_login_screen and self.restart_button.visible:
                self.restart_button.draw(self.screen)
            if self.show_login_screen:
                self.draw_login_screen()
            if self.leaderboard_button.clicked:
                self.show_leaderboard()
            if self.back_button.clicked:
                self.leaderboard_button.clicked = False
            pygame.display.update()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()
