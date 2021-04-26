import cv2
import numpy as np
import imutils
import RPi.GPIO as GPIO
import time

#Capture video
cap= cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

#Dimensions de la fenetre
largueur = 640
hauteur = 480

#Precision toleree
precision = 80

#Fonction convertissant un angle en impulsion pour le servomoteur
def angle_to_percent (angle) :
    
    start = 4
    end = 12.5
    ratio = (end - start)/180

    angle_as_percent = angle * ratio

    return start + angle_as_percent

GPIO.setmode(GPIO.BOARD) #Utilisation de la numerotation board du GPIO
GPIO.setwarnings(False) #Desactivation des avertissements lies au GPIO

#Les servos des yeux sont sur les pins 18 et 32
broche_servo_x_oeil = 18
broche_servo_y_oeil = 32
#La led est sur la pin 37
led_broche = 37

#La frequence du servo
frequence = 50

#Declaration des broches des composants
GPIO.setup(broche_servo_x_oeil, GPIO.OUT)
GPIO.setup(broche_servo_y_oeil, GPIO.OUT)
GPIO.setup(led_broche, GPIO.OUT)

#Declaration des broches PWM pour les servo
servo_x_oeil = GPIO.PWM(broche_servo_x_oeil, frequence)
servo_y_oeil = GPIO.PWM(broche_servo_y_oeil, frequence)

#intialisation : regard au centre
angle_x = 55
angle_y = 80

#Allumage de la led dans l'oeil
GPIO.output(led_broche, GPIO.HIGH)

while True:
     #Retour video
     _,frame= cap.read()
     #Redimensionnement de l'image
     resized = cv2.resize(frame, (largueur, hauteur))
     #Modification des couleurs de l'image en HSV
     hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    
     #Bornes du rouge d'une boite Raspberry
     lower_red = np.array([160,100,65])
     upper_red = np.array([255,255,255])
     
     #Application du masque
     mask = cv2.inRange(hsv,lower_red,upper_red)

     #Detection des contours
     cnts = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
     cnts = imutils.grab_contours(cnts)

     for c in cnts:
         area = cv2.contourArea(c) #Aire des contours
         if area > 5000: #Application d'un filtre pour ne garder que les gros contours
             
             #Afficahge des contours
             cv2.drawContours(resized,[c],-1,(0,255,0), 3)
             
             #Recuperation du centre du contour
             M = cv2.moments(c)
             cx = int(M["m10"]/ M["m00"])
             cy = int(M["m01"]/ M["m00"])
             
             #tracage d'un cercle au centre du contours
             cv2.circle(resized,(cx,cy),7,(255,255,255),-1)
             
             #Determination de la direction dans laquelle faire tourner les servos pour suivre le contours
             if cx > (largueur+precision)/2:
                 #print('droite')
                 #print(cx)
                 angle_x = angle_x - 1
                 
                 if angle_x < 25:
                    angle_x = 25
                 #print(angle)
            
             if cx < (largueur-precision)/2:
                 #print('gauche')
                 #print(cx)
                 angle_x = angle_x + 1
                
                 if angle_x > 80:
                    angle_x = 80
                 #print(angle)
            
             if cy > (hauteur+precision)/2:
                 #print('droite')
                 #print(cx)
                 angle_y = angle_y - 1
                 
                 if angle_y < 70:
                    angle_y = 70
                 #print(angle)
            
             if cy < (hauteur-precision)/2:
                 #print('gauche')
                 #print(cx)
                 angle_y = angle_y + 1
                
                 if angle_y > 90:
                    angle_y = 90
                 #print(angle)
             
             #Deplacement des yeux
             servo_x_oeil.start(angle_to_percent(angle_x))
             servo_y_oeil.start(angle_to_percent(angle_y))
             time.sleep(0.008)
             #Eteignage des servos des yeux (limitation des tremblements)
             servo_x_oeil.ChangeDutyCycle(0)
             servo_y_oeil.ChangeDutyCycle(0)
             time.sleep(0.008)

     #Affichage de la video
     cv2.imshow('Video', resized)
    
     #Si l'utilisateur appui sur echap le programme se coupe
     k = cv2.waitKey(5)
     if k == 27:
         break
        
#Destruction des fenetres
cv2.destroyAllWindows()