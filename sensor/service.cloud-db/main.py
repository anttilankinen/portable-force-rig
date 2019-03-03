import os
import csv
import json
import sqlite3
from flask import Flask, request
from pymongo import MongoClient

MLAB_DB = os.getenv('MLAB_DB')
MLAB_HOST = os.getenv('MLAB_HOST')
MLAB_PORT = int(os.getenv('MLAB_PORT'))
MLAB_USER = os.getenv('MLAB_USER')
MLAB_PASS = os.getenv('MLAB_PASS')

def readDb():

    print('Connecting to SQLite database..')
    sqlite_conn = sqlite3.connect('./data/readings.sqlite')
    cursor = sqlite_conn.cursor()

    print('Reading from SQLite database..')
    cursor.execute('SELECT * FROM database')
    data = cursor.fetchall()

    sqlite_conn.commit()
    sqlite_conn.close()
    return data

def cleanDb():

    print('Cleaning SQLite database..')
    sqlite_conn = sqlite3.connect('./data/readings.sqlite')
    cursor = sqlite_conn.cursor()
    cursor.execute('DELETE FROM database')
    sqlite_conn.commit()
    sqlite_conn.close()

def uploadToCloud(documents):

    print('Connecting to MongoDB..')
    client = MongoClient(MLAB_HOST, MLAB_PORT)
    db = client[MLAB_DB]
    db.authenticate(MLAB_USER, MLAB_PASS)

    print('Inserting documents to MongoDB database..')
    readings = db.readings
    result = readings.insert_many(documents)

    print('Closing connectiong to MongoDB..')
    client.close()

def upload():

    db_data = readDb()

    print('Formatting data..')
    documents = []
    for row in db_data:
        id, date_time, ant_size, row_data, file_name = row
        data_array = json.loads(row_data)
        new_document = {
            'id': id,
            'dateTime': date_time,
            'antSize': ant_size,
            'data': data_array,
            'fileName': file_name
        }
        documents.append(new_document)

    if documents:
        try:
            uploadToCloud(documents)
            # cleanDb()
            print('Data upload complete!')

        except Exception as error:
            print(error.message)
            raise

    else:
        print('Nothing to upload..')

def create_csv():
    print('Connecting to MongoDB..')
    client = MongoClient(MLAB_HOST, MLAB_PORT)
    db = client[MLAB_DB]
    db.authenticate(MLAB_USER, MLAB_PASS)

    try:
        print('Retrieving documents from MongoDB database..')
        readings = db['readings']
        csv_file = open('temp.csv', 'w')
        writer = csv.writer(csv_file)

        writer.writerow(['Date Time', 'Ant Size', 'Force Readings'])
        for document in readings.find():
            writer.writerow([document['dateTime'], document['antSize'], *document['data']])

        csv_file.close()
        print('Closing connectiong to MongoDB..')
        client.close()

    except Exception as error:
        print(error.message)
        raise

def send_email(email):
    print('Sending email..')
    os.remove('temp.csv')

if __name__ == '__main__':

    app = Flask(__name__)

    @app.route('/upload')
    def data_upload():
        upload()
        return 'Data upload complete!'

    @app.route('/csv')
    def email_csv():
        email = request.args['email']
        create_csv()
        send_email(email)
        return f'CSV sent to {email}!'

    @app.errorhandler(Exception)
    def unhandled_exception(err):
        return 'Error occured!', 500

    app.run(host='0.0.0.0', port=80)
