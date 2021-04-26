import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import RPi.GPIO as GPIO
import os
import time
import cgi

#Pour la voix
from espeak import espeak

##########################################
#########DECLARATION DES VARIABLES########
##########################################

#Valeurs d'angles limites des servos
hauteur_max_yeux = 90
hauteur_min_yeux = 70
hauteur_moyennes_yeux = 85

gauche_max_yeux = 80
droite_max_yeux = 25
centre_x_yeux = 55

bouche_fermee = 60
bouche_ouverte = 20

angle_x = centre_x_yeux
angle_y = hauteur_moyennes_yeux

##########################################
###DECLARATION DES SERVOS ET DE LA LED####
##########################################

#Les servos des yeux sont sur les pins 18 et 32
broche_servo_x_oeil = 18
broche_servo_y_oeil = 32
#Le servo de la bouche est sur la pin 29
broche_bouche = 29
#La led est sur la pin 37
led_broche = 37
#La led du socle est sur la pin
led_socle = 7

#La frequence des servo
frequence = 50

GPIO.setmode(GPIO.BOARD) #Use Board numerotation mode
GPIO.setwarnings(False) #Disable warnings

#Declaration des broches des composants
GPIO.setup(broche_servo_x_oeil, GPIO.OUT)
GPIO.setup(broche_servo_y_oeil, GPIO.OUT)
GPIO.setup(broche_bouche, GPIO.OUT)
GPIO.setup(led_broche, GPIO.OUT)
GPIO.setup(led_socle, GPIO.OUT)

#Declaration des broches PWM pour les servo
servo_x_oeil = GPIO.PWM(broche_servo_x_oeil, frequence)
servo_y_oeil = GPIO.PWM(broche_servo_y_oeil, frequence)
servo_bouche = GPIO.PWM(broche_bouche, frequence)

#Fonction convertissant un angle en impulsion pour le servomoteur
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180

    angle_as_percent = angle * ratio

    return start + angle_as_percent

##########################################
###################SETUP##################
##########################################

def regard_au_centre():
    #Fermeture de la bouche
    servo_bouche.start(angle_to_percent(bouche_fermee))
    time.sleep(1)
    servo_bouche.ChangeDutyCycle(0)

    #Regard au centre
    servo_x_oeil.start(angle_to_percent(centre_x_yeux))
    servo_y_oeil.start(angle_to_percent(hauteur_moyennes_yeux))
    time.sleep(1)
    servo_x_oeil.ChangeDutyCycle(0)
    servo_y_oeil.ChangeDutyCycle(0)

regard_au_centre()

##########################################
#################PAGE HTML################
##########################################

PAGE="""\
<html>
<style>
      body {background-color:#202020;}
</style>

<body>

<center><h1><FONT face="Verdana" color="white">BILBOT</FONT></h1>
<p>
<img src="stream.mjpg" width="640" height="480">
</p>

<FONT face="Verdana" color="#7D7DFF">
<p>
LED de l'oeil : <button onclick="window.location.href = '/on_led_oeil';">ON</button> <button onclick="window.location.href = '/off_led_oeil';">OFF</button>
</p>
<p>
LED du socle : <button onclick="window.location.href = '/on_led_socle';">ON</button> <button onclick="window.location.href = '/off_led_socle';">OFF</button>
</p>

<p><h3>DEPLACEMENT DES YEUX</h3></p>

<p>
Deplacement horizontal :
<button onclick="window.location.href = '/horizontale_full_gauche';">FULL GAUCHE</button>
<button onclick="window.location.href = '/horizontale_superieur';">GAUCHE</button>
<button onclick="window.location.href = '/horizontale_centre';">CENTRE</button>
<button onclick="window.location.href = '/horizontale_inferieur';">DROITE</button>
<button onclick="window.location.href = '/horizontale_full_droite';">FULL DROITE</button>
</p>

<p>
Deplacement vertical :
<button onclick="window.location.href = '/vertical_inferieur';">BAS</button>
<button onclick="window.location.href = '/vertical_superieur';">HAUT</button>
</p>

<p><h3>FAIRE PARLER BILBOT</h3></p>

<p><button onclick="window.location.href = '/dire1';">JE SUIS BILBOT</button></p>

</FONT>
</center>


</body>
</html>
"""

class StreamingOutput(object):
    
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
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

class StreamingHandler(server.BaseHTTPRequestHandler):
    
    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()
    
    def do_GET(self):
        
        global angle_x
        global angle_y
        
        status = ''
        
        #Parametres de la voix de base
        vitesse = '150'
        volume = '300'
        langue = 'fr'
             
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
            
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            
        elif self.path == '/stream.mjpg':
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
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        
        elif self.path=='/on_led_oeil':
            GPIO.output(led_broche, GPIO.HIGH)
            status='LED is On'
            self._redirect('/')
            
        elif self.path=='/off_led_oeil':
            GPIO.output(led_broche, GPIO.LOW)
            status='LED is Off'
            self._redirect('/')
        
        elif self.path=='/on_led_socle':
            GPIO.output(led_socle, GPIO.HIGH)
            status='LED is On'
            self._redirect('/')
            
        elif self.path=='/off_led_socle':
            GPIO.output(led_socle, GPIO.LOW)
            status='LED is Off'
            self._redirect('/')
            
        elif self.path=='/horizontale_superieur':
            angle_x += 5
            
            if angle_x > gauche_max_yeux:
                angle_x = gauche_max_yeux
            
            print(angle_x)
            
            #Deplacement des yeux
            servo_x_oeil.start(angle_to_percent(angle_x))
            time.sleep(0.1)
            #Eteignage des servos des yeux (limitation des tremblements)
            servo_x_oeil.ChangeDutyCycle(0)
            self._redirect('/')
            
        elif self.path=='/horizontale_inferieur':
            angle_x -= 5
            
            if angle_x < droite_max_yeux:
                angle_x = droite_max_yeux
            
            print(angle_x)
            
            #Deplacement des yeux
            servo_x_oeil.start(angle_to_percent(angle_x))
            time.sleep(0.1)
            #Eteignage des servos des yeux (limitation des tremblements)
            servo_x_oeil.ChangeDutyCycle(0)
            self._redirect('/')
        
        elif self.path=='/horizontale_full_gauche':
            angle_x = gauche_max_yeux
            
            print(angle_x)
            
            #Deplacement des yeux
            servo_x_oeil.start(angle_to_percent(angle_x))
            time.sleep(0.1)
            #Eteignage des servos des yeux (limitation des tremblements)
            servo_x_oeil.ChangeDutyCycle(0)
            self._redirect('/')
            
        elif self.path=='/horizontale_full_droite':
            angle_x = droite_max_yeux
            
            print(angle_x)
            
            #Deplacement des yeux
            servo_x_oeil.start(angle_to_percent(angle_x))
            time.sleep(0.1)
            #Eteignage des servos des yeux (limitation des tremblements)
            servo_x_oeil.ChangeDutyCycle(0)
            self._redirect('/')
            
        elif self.path=='/horizontale_centre':
            angle_x = centre_x_yeux
            
            print(angle_x)
            
            #Deplacement des yeux
            servo_x_oeil.start(angle_to_percent(angle_x))
            time.sleep(0.1)
            #Eteignage des servos des yeux (limitation des tremblements)
            servo_x_oeil.ChangeDutyCycle(0)
            self._redirect('/')
        
        elif self.path=='/vertical_superieur':
            angle_y += 2
            
            if angle_y > hauteur_max_yeux:
                angle_y = hauteur_max_yeux
            
            print(angle_y)
            
            #Deplacement des yeux
            servo_y_oeil.start(angle_to_percent(angle_y))
            time.sleep(0.1)
            #Eteignage des servos des yeux (limitation des tremblements)
            servo_y_oeil.ChangeDutyCycle(0)
            self._redirect('/')
            
        elif self.path=='/vertical_inferieur':
            angle_y -= 2
            
            if angle_y < hauteur_min_yeux:
                angle_y = hauteur_min_yeux
            
            print(angle_y)
            
            #Deplacement des yeux
            servo_y_oeil.start(angle_to_percent(angle_x))
            time.sleep(0.1)
            #Eteignage des servos des yeux (limitation des tremblements)
            servo_y_oeil.ChangeDutyCycle(0)
            self._redirect('/')
            
        elif self.path=='/dire1':
            
            text = "je suis bilbotte"
            print(text)
            text_coupe = text.split(' ')
            
            for i in text_coupe:
                #ouverture de la bouche
                servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
                os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
                #fermeture de la bouche
                servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
                time.sleep(0.05)
            
            servo_bouche.ChangeDutyCycle(0)
            
            self._redirect('/')

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()