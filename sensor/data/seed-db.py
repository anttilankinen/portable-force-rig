import json
import sqlite3

def main():

    sqlite_conn = sqlite3.connect('readings.sqlite')
    cursor = sqlite_conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS data (
        ant_size INTEGER,
        readings TEXT
    )''')

    print('Inserting into table: data')
    readings = [80.22, 60.56, 40.82]
    readings_str = json.dumps(readings)
    cursor.execute('INSERT INTO data (ant_size, readings) VALUES (?, ?)', (1.76, readings_str))

    cursor.execute('SELECT * FROM data')
    data = cursor.fetchall()
    print(data)

    sqlite_conn.commit()
    sqlite_conn.close()

if __name__ == '__main__':
    main()
