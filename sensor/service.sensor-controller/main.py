import random
from flask import Flask

if __name__ == '__main__':

    app = Flask(__name__)

    @app.route('/start')
    def start():
        value = random.uniform(10, 200)
        return f'Start reading from sensor.. Reading: {round(value, 2)}'

    @app.route('/stop')
    def stop():
        return 'Stop reading from sensor..'

    app.run(host='0.0.0.0', port=80)
