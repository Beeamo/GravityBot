import sqlite3

db_path = "database.sqlite"

class userdatabase():
    def __init__(self):
        with sqlite3.connect(db_path) as conn:
            self.conn = conn
            self.create_table()


    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users (DiscordID TEXT PRIMARY KEY)''')
        self.conn.commit()

    def verifyusers(self, idlist):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * from Users''')
        rows = cursor.fetchall()
        db_list = [row[0] for row in rows]
        for id in idlist:
            if id in db_list:
                continue
            cursor.execute("INSERT INTO Users (DiscordID) VALUES (?)", (id,))
        self.conn.commit()

    def adduser(self, userid):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Users (DiscordID) VALUES (?)", (userid,))
        self.conn.commit()

    def getusers(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * from Users''')
        rows = cursor.fetchall()
        db_list = [row[0] for row in rows]
        return db_list





