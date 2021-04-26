import cv2
import os
import RPi.GPIO as GPIO
import time
from espeak import espeak

#valeurs d'angle d'ouverture et de fermeture de la bouce
ouverte = 20
ferme = 60

vitesse = '150'
volume = '300'
langue = 'fr'

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

#Le servo de la bouche est sur la pin 29
pwm_gpio = 29

frequence = 50
GPIO.setup(broche_servo_x_oeil, GPIO.OUT)
GPIO.setup(broche_servo_y_oeil, GPIO.OUT)
GPIO.setup(led_broche, GPIO.OUT)
servo_x_oeil = GPIO.PWM(broche_servo_x_oeil, frequence)
servo_y_oeil = GPIO.PWM(broche_servo_y_oeil, frequence)

GPIO.setup(pwm_gpio, GPIO.OUT)
pwm = GPIO.PWM(pwm_gpio, frequence)
pwm.start(angle_to_percent(ferme))
time.sleep(0.5)
pwm.ChangeDutyCycle(0)

#intialisation : regard au centre
angle_x = 55
angle_y = 80
servo_x_oeil.start(angle_to_percent(angle_x))
servo_y_oeil.start(angle_to_percent(angle_y))
time.sleep(1)
servo_x_oeil.ChangeDutyCycle(0)
servo_y_oeil.ChangeDutyCycle(0)

#Allumage de la LED
GPIO.output(led_broche, GPIO.HIGH)

#Classifier utilise
cascPath = "/home/pi/Desktop/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
#Capture video
video_capture = cv2.VideoCapture(0)

start_time = time.time()

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(60, 60),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h),(0,255,0), 2)
        # Display the resulting frame
    
    actual_time = time.time()
    intervalle = 8
    
    if actual_time > start_time + intervalle:
        text = "je vois "+str(len(faces))+" personnes"
        print(text)
        text_coupe = text.split(' ')
        
        for i in text_coupe:
            #ouverture de la bouche
            pwm.ChangeDutyCycle(angle_to_percent(ouverte))
            os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
            #fermeture de la bouche
            pwm.ChangeDutyCycle(angle_to_percent(ferme))
            time.sleep(0.05)
        
        pwm.ChangeDutyCycle(0)
        start_time = time.time()
        
    cv2.imshow('Video', frame)
    
    k = cv2.waitKey(5)
    if k == 27:
         break
    
cv2.destroyAllWindows()