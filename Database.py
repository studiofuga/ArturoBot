import logging
import sqlite3
import os.path


class Database:
    def __init__(self):
        if not os.path.isfile("arturo.db"):
            self.db = self._create("arturo.db")
        else:
            self.db = sqlite3.connect("arturo.db", check_same_thread=False)

    def _create(self, filename : str) -> sqlite3.Connection:
        con = sqlite3.connect(filename, check_same_thread=False)
        schema = "arturo.schema"
        with open(schema, mode="r") as file:
            ddl = file.read()
        con.executescript(ddl)

        return con

    def check_user(self, user_id : int):
        cur = self.db.cursor()
        users = cur.execute("SELECT id FROM Users WHERE id=?", (user_id,))\
            .fetchall()
        if len(users) != 1:
            return False
        return True

