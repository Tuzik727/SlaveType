# SlaveType Documentation

## Executive Overview

SlaveType is a sophisticated typing test application, meticulously developed using the Pygame library. It features a minimalistic design, yet is enriched with a plethora of features that offer an immersive platform for users to enhance their typing skills.

## Initialization Instructions

### System Prerequisites

Before installing SlaveType, ensure the following requirements are met:

- Python 3.x environment is established on the host system.
- Pygame library, version 2.0.0 or higher, installed as stipulated in `requirements.txt`.

### Deployment Procedure

To install SlaveType, follow the steps below:

1. Download the latest release from the [Releases page](https://github.com/Tuzik727/SlaveType/releases/tag/1.0.0).
2. Unzip the downloaded package.
3. Run `SlaveType.exe`.

## Module Synopsis: Game Structure

The Game module is the core of the SlaveType application. It handles the initial setup, captures user inputs, governs game mechanics, renders visual elements, and interacts with the database to archive and retrieve user performance data.

### Class: `SlaveType`

#### Functional Overview

The `SlaveType` class is responsible for managing the game's operational state, event handling, and the rendering process.

#### Initialization Methods

- `__init__`: Configures the gaming environment, establishes database connectivity, and instantiates interactive game elements such as buttons.

#### Game Execution Flow

- `run`: Starts the main game loop, which includes event handling and visual rendering, until the game is exited.
- `dynamic_run_events(self)`: Handles dynamic running of events and updates the screen accordingly.

- `restart`: Resets the game state, allowing a new typing test to begin.

#### Event Management

- `handle_events`: Acts as the main event handler, delegating to specific event handling functions.
- `handle_keydown_event`: Captures keyboard strokes during typing tests.
- `handle_mousedown_event`: Handles mouse click events for buttons such as login, signup, and restart.
- `handle_video_resize_event`: Adjusts game components in response to changes in window size.
- `handle_difficulty_event(self, event)`: Handles events related to difficulty selection.
- `handle_login_events(self)`: Handles events on the login screen.
- `handle_login_keydown_event(self, event)`: Processes keydown events on the login screen's input fields.

#### Rendering Operations
- `render_text`: Renders text on the screen with the given properties and handles the visibility of the text cursor.
- `draw_login_screen`: Displays the login interface with input fields and buttons.
- `display_time`: Updates and shows the on-screen timer.
- `display_statistics`: Displays typing statistics such as WPM and accuracy.
- `show_leaderboard`: Displays the leaderboard with user scores.

#### Statistical Computation and Database Interactions

- `user_login`: Authenticates the user with the provided username and password.
- `user_signup`: Registers a new user with the given username and password.

- `save_user_statistics`: Records the session's statistical data in the database.
- `calculate_statistics`: Computes typing accuracy and words-per-minute (WPM) metrics.

#### Supplementary Methods

- `get_words`: Retrieves a random sentence from the database for the typing test.
- `get_scaled_font_size`: Calculates an optimal font size relative to screen resolution.
- `add_character_at_cursor`: Inserts a character into the input text at the cursor's position.
- `remove_character_at_cursor`: Removes a character from the input text at the cursor's position.
- `get_relative_pos`: Calculates the position on the screen as a percentage of the screen dimensions.

### Database Interactions

The `SlaveType` application leverages the `Database` class for all database operations. This class is responsible for establishing a connection to a MySQL database and executing various queries to manage user data and game statistics.

#### Class: `Database`

##### Initialization
- `__init__(self, host, user, passwd, dbname)`: Establishes a new database connection using the provided credentials.

##### Connection Management
- `ensure_connection(self)`: Checks the database connection and attempts to reconnect if it has been lost.

##### Sentence Management
- `insert_sentence(self, sentence)`: Inserts a sentence and its word count into the 'sentences' table.
- `get_random_sentence_by_word_count(self, count)`: Retrieves a random sentence with the specified word count from the database.

##### User Management
- `insert_user(self, username, password)`: Adds a new user with the given username and password.
- `get_user_id_by_username(self, username)`: Fetches the user ID based on the provided username.
- `verify_user_credentials(self, username, password)`: Verifies user credentials and returns the user ID if valid.
- `check_user_credentials(self, username, password)`: Checks if the provided username and password are correct.
- `create_user_account(self, username, password)`: Creates a new user account.

##### Statistical Data
- `insert_user_statistics(self, user_id, game_id, wpm, accuracy, play_time)`: Inserts typing test statistics for a user into the database.
- `get_top_scores(self, limit)`: Retrieves the top scores from the database.
- `get_top_daily_scores(self, limit)`: Fetches the top daily scores.

## UI Components

### Class: `DifficultyButton`

The `DifficultyButton` class is a custom UI component used for selecting the difficulty level in the `SlaveType` application. It is built using the Pygame library and provides interactive buttons with hover and click effects.

#### Initialization
- `__init__(self, x, y, width, height, text='', color)`: Initializes a new button with the specified position, size, text, and color.

#### Attributes
- `rect`: The rectangular area representing the button's bounds.
- `text`: The text displayed on the button.
- `color`: The background color of the button when not hovered or clicked.
- `clicked`: A boolean indicating whether the button has been clicked.
- `hover`: A boolean indicating whether the mouse is currently hovering over the button.
- `default_color`: The default color of the button.
- `hover_color`: The color of the button when the mouse hovers over it.
- `font_color`: The color of the text on the button.
- `font`: The font used for the button's text.

#### Methods
- `draw(self, screen)`: Renders the button on the provided Pygame screen surface, changing color based on the hover state.
- `update(self, mouse_pos)`: Updates the button's hover state based on the current mouse position.
- `handle_event(self, event)`: Handles mouse events, updating the button's clicked state if it is clicked.
#### Dependencies
- Python package `mysql-connector-python` is used for MySQL database interactions.

This class is instantiated as `db` in the `SlaveType` class and is used to facilitate all database-related operations within the application, such as authenticating users, storing game statistics, and providing content for typing tests.
## Dependency List

- Pygame: Used for graphical rendering and managing user interactions.
- mysql-connector-python: Enables connectivity with MySQL databases.

Make sure to install all required dependencies listed in `requirements.txt` before running the game.

### Starting the Game
- check README.md