#! /usr/bin/python
# -*- coding: utf-8 -*-
import time

print "Content-Type: text/html\n"
print """
<!DOCTYPE html>
<html>
 <head>
 <meta charset="UTF-8">
 <title>Une page Web</title>
 </head>

 <body>
 <h1>Une page Web avec CGI-Python</h1>
 <p>Heure courante {}</p>
 <center><img src="stream.mjpg" width="640" height="480"></center>
 </body>
</html>

""".format(time.strftime('%H:%M:%S'))

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
