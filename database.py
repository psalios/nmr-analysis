#!/usr/bin/python

import MySQLdb

from config import Properties

class Database:

    host = Properties.GetProperty("db.host")
    port = int(Properties.GetProperty("db.port"))
    db = Properties.GetProperty("db.name")
    username = Properties.GetProperty("db.username")
    password = Properties.GetProperty("db.password")

    @staticmethod
    def GetConnection():
        return MySQLdb.connect(
            host   = Database.host,
            port   = Database.port,
            db     = Database.db,
            user   = Database.username,
            passwd = Database.password
        )

# conn = Database.GetConnection()
# query = "SELECT name FROM user"
# cursor = conn.cursor()
# cursor.execute(query)
# for name in cursor.fetchall():
#     print(name)
# conn.close()
