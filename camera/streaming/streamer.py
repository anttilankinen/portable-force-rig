import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        # seconds = the duration of the memory held in the stream memory
        self.buffer = picamera.PiCameraCircularIO(camera, seconds=20)
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
        #EXTRA CODE (NOT NEEDED)
        # if self.path == '/':
        #     self.send_response(301)
        #     self.send_header('Location', '/index.html')
        #     self.end_headers()
        # elif self.path == '/index.html':
        #     content = PAGE.encode('utf-8')
        #     self.send_response(200)
        #     self.send_header('Content-Type', 'text/html')
        #     self.send_header('Content-Length', len(content))
        #     self.end_headers()
        #     self.wfile.write(content)

        #Setting the path of the stream
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
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
                    print('Stream successfully started')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

#Booting up the camera and settings
with picamera.PiCamera(resolution='640x480', framerate=90) as camera:
    #The Streaming Output
    output = StreamingOutput()
    #Begin recording
    camera.start_recording(output, format='mjpeg')
    try:
        #Target address (pi ip:8000)
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()