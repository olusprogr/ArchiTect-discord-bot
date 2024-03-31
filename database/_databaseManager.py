import sqlite3
import time
import random


class Database:
    db = None
    c = None

    def __init__(self, file: str):
        self.db = sqlite3.connect(file)
        self.c = self.db.cursor()

    def close(self):
        self.db.commit()
        self.db.close()

    def saveChanges(self):
        self.db.commit()

    def getConnection(self):
        return self.db

    def getCursor(self):
        return self.c


def getCurrentTime() -> str:
    t = time.localtime()
    current_time = time.asctime(t)
    return current_time


class Economy:
    db = None
    cursor = None
    connection = None

    def __init__(self, database: Database):
        self.connect = database.getConnection()
        self.cursor = database.getCursor()
        self.db = database

    def randomNum(self, a, b) -> int:
        return random.randint(a, b)

    def insertNewColumn(self, table, columnName, dataType) -> None:
        self.cursor.execute(
            f"""
            ALTER TABLE {table}
            ADD COLUMN {columnName} {dataType};
            """
        )

    def insertValue(self, author_id: int) -> None:
        self.cursor.execute(
            f"""
            INSERT OR IGNORE INTO users (user_id) VALUES (?)
            """, (author_id,)
        )
        randomNum = random.randint(1, 3)
        self.cursor.execute(
            f"""
            UPDATE users SET msg_count = msg_count + 1, xp = xp + {randomNum} WHERE user_id = {author_id}
            """
        )
        self.db.saveChanges()

    def insertValueIntoCredits(self, table: str, author_id: int):
        self.cursor.execute(
            f"""
            INSERT OR IGNORE INTO {table} (user_id) VALUES (?);
            """, (author_id,)
        )
        aswToReturn = self.randomNum(1, 5)
        self.cursor.execute(
            f"""
            UPDATE {table} SET credits = credits + {aswToReturn} WHERE user_id = {author_id};
            """
        )
        self.db.saveChanges()
        res = self.cursor.execute(
            f"""
            SELECT credits FROM {table} WHERE user_id = {author_id};
            """
        )
        return aswToReturn, res.fetchone()[0]

    def getUserXP(self, user_id: int) -> int:
        res = self.cursor.execute(
            f"""
            SELECT xp FROM users WHERE user_id = {user_id}
            """
        )
        return res.fetchone()


class Administrator:
    db = None
    cursor = None
    connection = None

    def __init__(self, database: Database):
        self.connect = database.getConnection()
        self.cursor = database.getCursor()
        self.db = database

    def createTable(self, name: str):
        self.cursor.execute(
            f"""
                    CREATE TABLE IF NOT EXISTS {name} (
                        username TEXT,
                        user_id TEXT,
                        admin INTEGER,
                        premium INTEGER
                        )
            """
        )

    def get(self, table: str, list = None) -> []:
        res = self.cursor.execute(
            f"""
                SELECT * FROM {table}
            """
        )
        datalist = []
        for dataset in res:
            datalist.append(dataset)
        return datalist

    def checkForAdmin(self, user_id: int, table: str) -> bool:
        res = self.cursor.execute(
            f"""
            SELECT username FROM {table}
            WHERE user_id = ? AND admin = 1
            """, (user_id,)
        )
        res = res.fetchone()
        if res:
            print("User found", res)
            return True
        else:
            print("User not found")
            return False

    def checkForPremium(self, user_id: int, table: str) -> bool:
        res = self.cursor.execute(
            f"""
            SELECT username FROM {table}
            WHERE user_id = ? AND premium = 1;
            """, (user_id,)
        )
        res = res.fetchone()
        if res:
            print("User found", res)
            return True
        else:
            print("User not found")
            return False

    def write(self, username: str, user_id: str, admin: bool, premium: bool) -> None:
        self.cursor.execute(
            f"""
            INSERT INTO user VALUES
            ('{username}', '{user_id}', '{admin}', '{premium}')
            """
        )
        self.db.saveChanges()

    def clear_log(self, table: str):
        self.cursor.execute(
            f"""
            DELETE FROM {table}
            """
        )
        self.db.saveChanges()
        return 'Logs cleared!'


class Log:
    db = None
    cursor = None
    connection = None

    def __init__(self, database: Database):
        self.connect = database.getConnection()
        self.cursor = database.getCursor()
        self.db = database

    def createTable(self, name: str):
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {name} (
                datetime TEXT,
                guild TEXT,
                username TEXT,
                command TEXT,
                add_content TEXT
                )
            """
        )

    def log(self, guild: str, username: str, command: str, add_content = None) -> bool:
        try:
            self.cursor.execute("INSERT INTO log VALUES (?, ?, ?, ?, ?)", (getCurrentTime(), guild, username,
                                                                           command, add_content,))
            self.db.saveChanges()
            return True
        except:
            return False
