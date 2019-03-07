import os
import csv
import json
import sqlite3
from flask import Flask, request
from pymongo import MongoClient
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders

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

def send_email(to_email):
    print('Crafting email..')

    SUBJECT = 'Portable Force Rig Data'
    FILENAME = 'temp.csv'
    FILEPATH = './temp.csv'
    FROM_EMAIL = os.getenv('EMAIL_ACC')
    EMAIL_PWD = os.getenv('EMAIL_PWD')
    TO_EMAIL = to_email
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587

    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = COMMASPACE.join([TO_EMAIL])
    msg['Subject'] = SUBJECT

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(FILEPATH, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=FILENAME)
    msg.attach(part)

    try:
        print('Sending email..')
        smtpserver = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.login(FROM_EMAIL, EMAIL_PWD)
        smtpserver.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        smtpserver.quit()

    except Exception as err:
        print(err)

    finally:
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
