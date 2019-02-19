import json
import sqlite3
from datetime import datetime


def main():

    sqlite_conn = sqlite3.connect('readings.sqlite')
    cursor = sqlite_conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS database (
        id TEXT,
        date_time TEXT,
        ant_size TEXT,
        readings TEXT
    )''')

    cursor.execute('SELECT * FROM database')
    data = cursor.fetchall()
    print(data)

    sqlite_conn.commit()
    sqlite_conn.close()


if __name__ == '__main__':
    main()
