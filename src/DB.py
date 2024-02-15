import datetime

import mysql.connector


class Database:
    def __init__(self, host, user, passwd, dbname):
        """
        Initializes a new instance of the class with the specified database connection parameters.

        :param host: The host of the database.
        :param user: The username for the database connection.
        :param passwd: The password for the database connection.
        :param dbname: The name of the database to connect to.
        """
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=dbname
        )

    def ensure_connection(self):
        """
        Ensure the database connection by pinging the database and reconnecting if the connection is lost.
        """
        try:
            self.db.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error:
            print("Database connection lost. Trying to reconnect...")
            self.db.reconnect(attempts=3, delay=5)

    def insert_sentence(self, sentence):
        """
        Inserts a given sentence and its word count into the 'sentences' table in the database.

        Parameters:
            self (obj): The instance of the class.
            sentence (str): The sentence to be inserted into the database.

        Returns:
            None
        """
        self.ensure_connection()
        word_count = len(sentence.split())
        cursor = self.db.cursor()
        query = "INSERT INTO sentences (sentence, word_count) VALUES (%s, %s)"
        cursor.execute(query, (sentence, word_count))
        self.db.commit()
        cursor.close()

    def get_random_sentence_by_word_count(self, count):
        """
        Retrieves a random sentence from the database based on the specified word count.

        Args:
            count (int): The word count of the desired sentence.

        Returns:
            str or None: The randomly selected sentence with the specified word count, or None if no such sentence is found.
        """
        self.ensure_connection()
        cursor = self.db.cursor()
        query = "SELECT sentence FROM sentences WHERE word_count = %s ORDER BY RAND() LIMIT 1"
        cursor.execute(query, (count,))
        sentence = cursor.fetchone()
        cursor.close()
        return sentence[0] if sentence else None

    def insert_user(self, username, password):
        """
        Inserts a new user into the database with the given username and password.

        :param username: the username of the new user
        :param password: the password of the new user
        :return: None
        """
        if username is None or password is None:
            return False
        self.ensure_connection()
        cursor = self.db.cursor()
        query = "INSERT INTO users (username, password) values (%s, %s)"
        cursor.execute(query, (username, password))
        self.db.commit()
        cursor.close()

    def insert_user_statistics(self, user_id: int, game_id: int, wpm: float, accuracy: float,
                               play_time: int):
        """
        Inserts user statistics into the database.

        Parameters:
            user_id (int): The ID of the user.
            game_id (int): The ID of the game.
            wpm (float): Words per minute typed by the user.
            accuracy (float): The accuracy of the user's typing.
            play_time (int): The duration of the game played in seconds.

        Returns:
            None
        """
        self.ensure_connection()
        cursor = self.db.cursor()
        query = """
            INSERT INTO UserStatistics (user_id, game_id, wpm, accuracy, play_time, date_played)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        date_played = datetime.datetime.now()  # Current date and time
        cursor.execute(query, (user_id, game_id, wpm, accuracy, play_time, date_played))
        self.db.commit()
        cursor.close()

    def get_user_id_by_username(self, username):
        """
        Retrieves the user id by the given username.

        Args:
            username (str): The username to look up in the database.

        Returns:
            int or None: The user id if found, otherwise None.
        """
        self.ensure_connection()
        cursor = self.db.cursor()
        query = "SELECT id FROM Users WHERE username = %s"
        cursor.execute(query, (username,))
        user_id = cursor.fetchone()
        cursor.close()
        return user_id[0] if user_id else None

    def verify_user_credentials(self, username, password):
        """
        Verify user credentials.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            int or bool: The user ID if credentials are valid, False otherwise.
        """
        if not username or not password:
            return False
        self.ensure_connection()
        cursor = self.db.cursor()
        query = "SELECT id FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else False

    def check_user_credentials(self, username, password):
        """
        Check user credentials.

        Args:
            self: The object itself.
            username: The username of the user.
            password: The password of the user.

        Returns:
            bool: True if the username and password match, False otherwise.
        """
        self.ensure_connection()
        cursor = self.db.cursor()
        query = "SELECT password FROM Users WHERE username = %s"
        cursor.execute(query, (username,))
        stored_password = cursor.fetchone()
        cursor.close()
        return stored_password and stored_password[0] == password

    def create_user_account(self, username, password):
        """
        Creates a user account with the given username and password.

        Parameters:
            username (str): The username for the new account.
            password (str): The password for the new account.

        Returns:
            None
        """
        hashed_password = password
        self.insert_user(username, hashed_password)

    def get_top_scores(self, limit=10):
        """
        Retrieves the top scores from the database.

        :param limit: int, the maximum number of scores to retrieve (default is 10)
        :return: list, a list of top scores including username, the best wpm, accuracy, and date played
        """
        self.ensure_connection()
        cursor = self.db.cursor()
        query = """
            SELECT u.username, s.wpm AS best_wpm, s.accuracy, s.date_played
            FROM Users u
            JOIN (
                SELECT user_id, wpm, accuracy, date_played
                FROM UserStatistics
                WHERE (user_id, wpm, date_played) IN (
                    SELECT user_id, MAX(wpm), date_played
                    FROM UserStatistics
                    GROUP BY user_id, DATE(date_played)
                )
            ) s ON u.id = s.user_id
            ORDER BY s.wpm DESC
            LIMIT %s;

        """
        cursor.execute(query, (limit,))
        scores = cursor.fetchall()
        cursor.close()
        return scores

    def get_top_daily_scores(self, limit=10):
        """
        Get the top daily scores from the database.

        Parameters:
            limit (int): The maximum number of scores to return. Defaults to 10.

        Returns:
            list: A list of tuples containing the top daily scores, each tuple containing the username, the best wpm, accuracy, and date played.
        """
        self.ensure_connection()
        cursor = self.db.cursor()
        query = """
            SELECT u.username, s.wpm AS best_wpm, s.accuracy, s.date_played
            FROM Users u
            JOIN (
                SELECT user_id, wpm, accuracy, date_played
                FROM UserStatistics
                WHERE (user_id, wpm, date_played) IN (
                    SELECT user_id, MAX(wpm), date_played
                    FROM UserStatistics
                    WHERE DATE(date_played) = CURDATE()
                    GROUP BY user_id, DATE(date_played)
                )
            ) s ON u.id = s.user_id
            ORDER BY s.wpm DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        scores = cursor.fetchall()
        cursor.close()
        return scores

    def close(self):
        """
        Closes the database connection.
        """
        self.db.close()
