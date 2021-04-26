import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np
from flask import Flask, render_template, request, Response, render_template_string
import os
from picamera import PiCamera
import RPi.GPIO as GPIO
from espeak import espeak
from googletrans import Translator

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

etat_led_oeil = False
etat_led_socle = False

#Parametres de la voix de base
vitesse = '150'
volume = '300'
langue = 'fr'

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
################APPLICATION###############
##########################################

vc = cv2.VideoCapture(0) 

app = Flask(__name__)

@app.route('/',methods = ['GET'])
def show_indexhtml():
    return render_template('index.html')

@app.route('/retour',methods = ['POST'])
def retour_indexhtml():
    return render_template('index.html')

def gen(): 
   """Video streaming generator function.""" 
   while True: 
       rval, frame = vc.read() 
       cv2.imwrite('pic.jpg', frame) 
       yield (b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')
       
@app.route('/video_feed') 
def video_feed(): 
   """Video streaming route. Put this in the src attribute of an img tag.""" 
   return Response(gen(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame') 

@app.route("/horizontal", methods=["POST"])
def horizontal():
    # Get slider Values
    slider = request.form["slider"]
    angle_x = int(slider)
            
    print(angle_x)
            
    #Deplacement des yeux
    servo_x_oeil.start(angle_to_percent(angle_x))
    time.sleep(0.1)
    #Eteignage des servos des yeux (limitation des tremblements)
    servo_x_oeil.ChangeDutyCycle(0)
    return show_indexhtml()

@app.route('/led_oeil', methods = ['POST'])
def allumage_led_oeil():
        global etat_led_oeil
        if etat_led_oeil == False:
            etat_led_oeil = True
            GPIO.output(led_broche, GPIO.HIGH)
            status='LED is On'
        else:
            etat_led_oeil = False
            GPIO.output(led_broche, GPIO.LOW)
            status='LED is Off'
        return show_indexhtml()
    
@app.route('/led_socle', methods = ['POST'])
def allumage_led_socle():
        global etat_led_socle
        if etat_led_socle == False:
            etat_led_socle = True
            GPIO.output(led_socle, GPIO.HIGH)
            status='LED is On'
        else:
            etat_led_socle = False
            GPIO.output(led_socle, GPIO.LOW)
            status='LED is Off'
        return show_indexhtml()

@app.route('/message', methods = ['POST'])
def lire_message():
        message = request.form['message']
        
        message_coupe = message.split(' ')
            
        for i in message_coupe:
            #ouverture de la bouche
            servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
            os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
            #fermeture de la bouche
            servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
            time.sleep(0.05)
            
        servo_bouche.ChangeDutyCycle(0)
        
        return show_indexhtml()

@app.route('/traduction', methods = ['POST'])
def traducteur_index():
    print('mode traducteur active')
    return '''
<!DOCTYPE html>
<html>
  <style>
      body {background-color:#202020;}
  </style>

  <body>
     <center><h1><FONT face="Verdana" color="white">BILBOT LE TRADUCTEUR</FONT></h1>
     <FONT face="Verdana" color="#FFF77D">
     
	  <form class="form-inline" method="POST" action="/dire_traduction">
	    <div class="form-group">
	  
	    <p><div class="input-group">
		<span class="input-group-addon">Langue d'entrée :</span>
		    <select name="langue_entree_select" class="selectpicker form-control">
		      <option value="FR">Français</option>
		      <option value="EN">Anglais</option>
		      <option value="PT">Portugais</option>
		      <option value="DE">Allemand</option>
		      <option value="ES">Espagnol</option>
		    </select>
	    </div></p>
	    
	    <p><div class="input-group">
		<span class="input-group-addon">Langue de sortie :</span>
		    <select name="langue_sortie_select" class="selectpicker form-control">
		      <option value="FR">Français</option>
		      <option value="EN">Anglais</option>
		      <option value="PT">Portugais</option>
		      <option value="DE">Allemand</option>
		      <option value="ES">Espagnol</option>
		    </select>
	    </div></p>
	    
	    <p><div class="input-group">
		<span class="input-group-addon">Vitesse :</span>
		    <select name="vitesse_select" class="selectpicker form-control">
		      <option value="rapide">rapide</option>
		      <option value="lente">lente</option>	      
		    </select>
	    </div></p>
	    
	    <input type="text" name = "text">
	    
	    <button type="submit" class="btn btn-default">GO</button>
	  </div>
	</form>
    
    <form method="POST" action="/retour">
        <p><input type="submit" value="Retour" /></p>
    </form>
    
  </body>
</html>
'''

@app.route('/dire_traduction', methods = ['POST'])
def dire_traduction():
    print('RESULTAT TRADUCTION')
    
    langue_entree=request.form['langue_entree_select']
    langue_sortie=request.form['langue_sortie_select']
    vitesse=request.form['vitesse_select']
    text=request.form['text']
    
    print(langue_entree, langue_sortie, vitesse)
    
    #declaration du traducteur
    trans= Translator()
    translation = trans.translate(text, src=langue_entree, dest=langue_sortie)
    #traduction du texte
    texte_traduit = translation.text
    print(texte_traduit)
                
    #decoupage mot par mot du texte
    parole = texte_traduit.split(' ')
    for i in parole:
        #ouverture de la bouche
        servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
        #lecture du mot en fonction de la vitesse choisie par l'utilisateur
        if vitesse == 'rapide':
            os.system('espeak -s '+'150'+' -a '+volume+' -z -v '+langue_sortie+' "'+i+'"')
        if vitesse == 'lente':
            os.system('espeak -s '+'20'+' -a '+volume+' -v '+langue_sortie+' "'+i+'"')
        #fermeture de la bouche
        servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
        time.sleep(0.05)
    
    servo_bouche.ChangeDutyCycle(0)
    return traducteur_index()
    
if __name__ == '__main__':
    app.run(host="172.16.5.114", port=5000)