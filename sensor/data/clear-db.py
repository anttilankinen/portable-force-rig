import json
import sqlite3

def main():

    sqlite_conn = sqlite3.connect('readings.sqlite')
    cursor = sqlite_conn.cursor()

    print('Clearing SQLite database..')
    cursor.execute('DELETE FROM data')

    sqlite_conn.commit()
    sqlite_conn.close()

if __name__ == '__main__':
    main()
