import mysql.connector


class Database:
    def __init__(self, host, user, passwd, dbname):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=dbname
        )

    def ensure_connection(self):
        try:
            self.db.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error as err:
            print("Database connection lost. Trying to reconnect...")
            self.db.reconnect(attempts=3, delay=5)

    def insert_sentence(self, sentence):
        self.ensure_connection()
        word_count = len(sentence.split())
        cursor = self.db.cursor()
        query = "INSERT INTO sentences (sentence, word_count) VALUES (%s, %s)"
        cursor.execute(query, (sentence, word_count))
        self.db.commit()
        cursor.close()

    def get_random_sentence_by_word_count(self, count):
        self.ensure_connection()
        cursor = self.db.cursor()
        query = "SELECT sentence FROM sentences WHERE word_count = %s ORDER BY RAND() LIMIT 1"
        cursor.execute(query, (count,))
        sentence = cursor.fetchone()
        cursor.close()
        return sentence[0] if sentence else None

    def close(self):
        self.db.close()
