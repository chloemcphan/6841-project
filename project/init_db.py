import sqlite3
from hashlib import sha256

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password, active) VALUES (?, ?, TRUE)",
            ('default', sha256('password123'.encode('utf-8')).digest()))

connection.commit()
connection.close()
