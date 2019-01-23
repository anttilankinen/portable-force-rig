import json
import sqlite3

def main():

    sqlite_conn = sqlite3.connect('readings.sqlite')
    cursor = sqlite_conn.cursor()

    cursor.execute('SELECT * FROM database')
    data = cursor.fetchall()
    print(data)

    sqlite_conn.commit()
    sqlite_conn.close()

if __name__ == '__main__':
    main()
