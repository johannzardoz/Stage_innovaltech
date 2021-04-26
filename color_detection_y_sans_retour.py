import cv2
import numpy as np
import imutils
import RPi.GPIO as GPIO
import time

#video
cap= cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

largueur = 640
hauteur = 480

precision = 80

#servo
def angle_to_percent (angle) :
    
    start = 4
    end = 12.5
    ratio = (end - start)/180 #Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent

GPIO.setmode(GPIO.BOARD) #Use Board numerotation mode
GPIO.setwarnings(False) #Disable warnings
#Use pin 18 for PWM signal
broche_servo_x_oeil = 18
broche_servo_y_oeil = 32
led_broche = 37

frequence = 50
GPIO.setup(broche_servo_x_oeil, GPIO.OUT)
GPIO.setup(broche_servo_y_oeil, GPIO.OUT)
GPIO.setup(led_broche, GPIO.OUT)
servo_x_oeil = GPIO.PWM(broche_servo_x_oeil, frequence)
servo_y_oeil = GPIO.PWM(broche_servo_y_oeil, frequence)

#intialisation : regard au centre
angle_x = 55
angle_y = 80
#servo_x_oeil.start(angle_to_percent(angle))
GPIO.output(led_broche, GPIO.HIGH)

while True:
     _,frame= cap.read()
     resized = cv2.resize(frame, (largueur, hauteur))
     hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

     lower_red = np.array([160,100,65])
     upper_red = np.array([255,255,255])

     mask = cv2.inRange(hsv,lower_red,upper_red)

     cnts = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
     cnts = imutils.grab_contours(cnts)

     for c in cnts:
         area = cv2.contourArea(c)
         if area > 5000:

             M = cv2.moments(c)

             cx = int(M["m10"]/ M["m00"])
             cy = int(M["m01"]/ M["m00"])
             
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
             
             servo_x_oeil.start(angle_to_percent(angle_x))
             servo_y_oeil.start(angle_to_percent(angle_y))
             time.sleep(0.008)
             servo_x_oeil.ChangeDutyCycle(0)
             servo_y_oeil.ChangeDutyCycle(0)
             time.sleep(0.008)