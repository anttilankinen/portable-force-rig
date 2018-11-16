import os
import random
import redis
import threading
from time import sleep
from flask import Flask

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))

if __name__ == '__main__':

    app = Flask(__name__)
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    reddis_channel = redis_client.pubsub()
    reddis_channel.subscribe('sensor-data')

    # start thread to read from GPIO
    @app.route('/start')
    def start():
        # read from GPIO
        value = random.uniform(10, 100)
        # publish to redis
        redis_client.publish('sensor-data', f'{round(value, 2)}')
        return f'Started reading from sensor..'

    # stop thread to read from GPIO
    @app.route('/stop')
    def stop():
        return 'Stopped reading from sensor..'

    app.run(host='0.0.0.0', port=80)
