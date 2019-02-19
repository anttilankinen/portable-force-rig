import os
import random
import time
import redis
import threading
from flask import Flask
from multiprocessing import Process


REDIS_PORT = int(os.getenv('REDIS_PORT'))

app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=REDIS_PORT, db=0)
reddis_channel = redis_client.pubsub()

process = None

def read_loop():
    while True:
        value = random.uniform(10, 100)
        redis_client.publish('sensor-data', f'{round(value, 2)}')
        time.sleep(1)

# start process to read from GPIO
@app.route('/start')
def start():
    # # read from GPIO
    global process
    if process is None:
        process = Process(target=read_loop)
        process.start()
        return 'Started reading from sensor..'
    return 'Sensor already running..'

# stop process to read from GPIO
@app.route('/stop')
def stop():
    global process
    if process is not None:
        process.terminate()
        process = None
        return 'Stopped reading from sensor..'
    return 'Sensor not running..'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
