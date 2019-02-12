#From main.py
import os
import time
import threading
from flask import Flask
import sys

#from streamer.py
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

app = Flask(__name__)

ELAPSED_TIME = 0
READ_THREAD = None
THREAD_IS_RUN = False
INTERV = 35

#Clipping handler

#Clipping function
def clip_buffer():
    global ELAPSED_TIME
    global THREAD_IS_RUN
    global INTERV
    i = 0

    while THREAD_IS_RUN:
        try:
            clipname = 'clip' + i +'.mjpeg'
            camera.wait_recording(35)
            output.buffer.copy_to(clipname)
            i+=1
            print(clipname + 'clipped')
            ELAPSED_TIME += INTERV
        except:
            print('error')

# start process
@app.route('/start')
def start():
    # read from GPIO
    global THREAD_IS_RUN
    global READ_THREAD
    global ELAPSED_TIME
    global output
    print('Clipping')

    if READ_THREAD is None:
        print('Clipping code')
        ELAPSED_TIME = 0
        #Clearing the buffer when pressing start
        output.buffer.clear()
        THREAD_IS_RUN = True
        READ_THREAD = threading.Thread(target=clip_buffer)
        READ_THREAD.start()
        return 'Start clippipng..'
    return 'Clipping already running..'

#Ending of process
@app.route('/stop')
def stop():
    # stop reading
    global THREAD_IS_RUN
    global READ_THREAD
    if READ_THREAD is not None:
        THREAD_IS_RUN = False
        READ_THREAD.join()
        READ_THREAD = None
        return 'Stopped clipping..'
    return 'Clipping not running..'

#Streaming class
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        # seconds = the duration of the memory held in the stream memory
        self.buffer = picamera.PiCameraCircularIO(camera, seconds=35)
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

#Server paths and error checks
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        #Setting the path of the stream
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                print('Stream successfully started')
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            print('Stream failed to start')
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':

    try:
        #Creating the server (streamer.py)
        #Booting up the camera and settings
        with picamera.PiCamera(resolution='640x480', framerate=90) as camera:
            #The Streaming Output
            output = StreamingOutput()
            #Begin recording
            camera.start_recording(output, format='mjpeg')
            try:
                # Target address (pi ip:8000)
                address = ('', 8000)
                server = StreamingServer(address, StreamingHandler)
                server.serve_forever()
                app.run(host='0.0.0.0', port=8001)
            finally:
                camera.stop_recording()

    except Exception as e:
        print(e)
        sys.exit(1)
