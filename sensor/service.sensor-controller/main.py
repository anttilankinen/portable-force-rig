import os
import random
import redis
import threading
from flask import Flask

REDIS_PORT = int(os.getenv('REDIS_PORT'))

app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=REDIS_PORT, db=0)
reddis_channel = redis_client.pubsub()

# start thread to read from GPIO
@app.route('/start')
def start():
    # read from GPIO
    value = random.uniform(10, 100)
    # publish to redis
    redis_client.publish('sensor-data', f'{round(value, 2)}')
    return 'Started reading from sensor..'

# stop thread to read from GPIO
@app.route('/stop')
def stop():
    return 'Stopped reading from sensor..'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
