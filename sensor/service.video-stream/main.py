#For Threading
import os
import time
import threading

#For streaming
import io
import simplejson as json
import picamera
import logging
import socketserver
from threading import Condition
from http import server

#For converting
import converter

#Global variables
ELAPSED_TIME = 0
READ_THREAD = None
THREAD_IS_RUN = False

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

#Clipping function
def clip_buffer(id):
    global ELAPSED_TIME
    global THREAD_IS_RUN

    print('Creating empty file')
    clipname = 'temp.h264'
    camera.start_recording(clipname, splitter_port=2)
    print('Recording')

    while THREAD_IS_RUN:
        try:
            print('Waiting')
            camera.wait_recording(10)
        except Exception as e:
            print(e)

    camera.stop_recording(splitter_port=2)
    print('Clipping completed')
    converter.convert(clipname, id)

#Server paths and error checks
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","*")
        self.send_header("Access-Control-Allow-Headers","*")
        self.end_headers()

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

        #End Process
        elif self.path == '/record/end':
            global THREAD_IS_RUN
            global READ_THREAD

            print('Stop')
            if READ_THREAD is not None:
                print('Stopping Clipping')
                try:
                    THREAD_IS_RUN = False
                    READ_THREAD.join()
                    READ_THREAD = None
                    self.send_response(200)
                    self.send_header("Access-Control-Allow-Origin","*")
                    self.send_header("Access-Control-Allow-Methods","*")
                    self.send_header("Access-Control-Allow-Headers","*")
                    self.end_headers()

                except Exception as e:
                    print(e)
                    self.send_response(500)
                    self.send_header("Access-Control-Allow-Origin","*")
                    self.send_header("Access-Control-Allow-Methods","*")
                    self.send_header("Access-Control-Allow-Headers","*")
                    self.end_headers()

        else:
            print('Stream failed to start')
            self.send_error(404)
            self.end_headers()

    def do_POST(self):
        #Start process
        if self.path == '/record/begin':
            global THREAD_IS_RUN
            global READ_THREAD
            global ELAPSED_TIME

            post_data = self.rfile.read(int(self.headers.get('Content-Length')))
            json_data = json.loads(post_data)
            if READ_THREAD is None:
                print('Begin Clipping')
                try:
                    print('Clipping')
                    ELAPSED_TIME = 0
                    THREAD_IS_RUN = True
                    READ_THREAD = threading.Thread(target=clip_buffer, args=(json_data['id'],))
                    READ_THREAD.start()
                    self.send_response(200)
                    self.send_header("Access-Control-Allow-Origin","*")
                    self.send_header("Access-Control-Allow-Methods","*")
                    self.send_header("Access-Control-Allow-Headers","*")
                    self.end_headers()

                except Exception as e:
                    print(e)
                    self.send_response(500)
                    self.send_header("Access-Control-Allow-Origin","*")
                    self.send_header("Access-Control-Allow-Methods","*")
                    self.send_header("Access-Control-Allow-Headers","*")
                    self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

#Booting up the camera and settings
with picamera.PiCamera(resolution='640x480', framerate=60) as camera:
    #The Streaming Output
    output = StreamingOutput()
    #Begin recording
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 7007)
        server = StreamingServer(address, StreamingHandler)
        print('Video streaming server running on port 7007')
        server.serve_forever()
    finally:
        camera.stop_recording()
