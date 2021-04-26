# coding=utf-8
import RPi.GPIO as GPIO
import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from espeak import espeak
import time
import os

#valeurs d'angle d'ouverture et de fermeture de la bouce
ouverte = 20
ferme = 60

#intervalle de temps entre 2 lecture du meme QR code
intervale = 8

GPIO.setmode(GPIO.BOARD) #Utilisation de la numérotation board du GPIO
GPIO.setwarnings(False) #Desactivation des avertissements liés au GPIO

#Fonction convertissant un angle en impulsion pour le servomoteur
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180 #Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent

#Le servo de la bouche est sur la pin 29
pwm_gpio = 29
#La frequence du servo
frequence = 50
#Declaration de la broche du servo
GPIO.setup(pwm_gpio, GPIO.OUT)
#Declaration de la broche PWM pour le servo
pwm = GPIO.PWM(pwm_gpio, frequence)

#Fermeture de la bouche
pwm.start(angle_to_percent(ferme))
time.sleep(0.5)
pwm.ChangeDutyCycle(0)

#Capture video
cap = cv2.VideoCapture(0)
font = cv2.FONT_HERSHEY_PLAIN

#Parametres de la voix
vitesse = '150'
volume = '300'
langue = 'fr'

#Temps actuel
start_time = time.time()

#Initialisation de l'ancien data (permettant de ne pas lire 2 fois a la suite le meme QR code
old_data = ''

while True:
    #Eteignage du servo de la bouche (pour limiter la nuisance sonore
    pwm.ChangeDutyCycle(0)
    #Recuperation de l'image
    _, frame = cap.read()
    #Detection des QR codes sur l'image
    decodedObjects = pyzbar.decode(frame)
    for obj in decodedObjects:
        #Prise du temps
        actual_time = time.time()
        #Affichage du texte du QR code sur l'image
        cv2.putText(frame, str(obj.data), (50, 50), font, 2,(255, 0, 0), 3)
        
        #Recuperation du texte
        data_r = obj.data
        
        #On verifie que soit le QR code n'est pas le meme que l'ancien, soit l'intervalle de temps est passee
        if data_r != old_data or start_time + intervale < actual_time :
            #L'ancien QR code devient le nouveau
            old_data = data_r
            #Reset du temps
            start_time = time.time()
            #Conversion du message en byte en string
            data_r = data_r.decode('UTF-8')
            #Coupage du texte du QR code en mot par mot
            data_spit = data_r.split(' ')
            for i in data_spit:
                #ouverture de la bouche
                pwm.ChangeDutyCycle(angle_to_percent(ouverte))
                #Lecture du mot
                os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
                #fermeture de la bouche
                pwm.ChangeDutyCycle(angle_to_percent(ferme))
                time.sleep(0.05)
    
    #Affichage de l'image
    cv2.imshow("affichage",frame)
    
    #Si l'utilisateur appui sur echap le programme se coupe
    k = cv2.waitKey(5)
    if k == 27:
        break

#Destruction des fenetres
cv2.destroyAllWindows()