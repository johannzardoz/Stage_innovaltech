import RPi.GPIO as GPIO
import time


#Set function to calculate percent from angle
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180 #Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent


GPIO.setmode(GPIO.BOARD) #Use Board numerotation mode
GPIO.setwarnings(False) #Disable warnings

#18 regard x
#32 regard y
#29 bouche
pwm_gpio = 29
frequence = 50
GPIO.setup(pwm_gpio, GPIO.OUT)
pwm = GPIO.PWM(pwm_gpio, frequence)

while True:
    
    #regard x : 55 centre, 80 gauche, 25 droite
    #regard y : 80 centre, 90 haut, 70 bas
    #bouche : 60 fermee, 20 ouverte
    #pwm.start(angle_to_percent(95))
    #time.sleep(1)
    
    #gauche
    #pwm.start(angle_to_percent(85))
    #time.sleep(1)
    
    #droite
    #pwm.start(angle_to_percent(25))
    #time.sleep(1)
    
    i = 60
    while i != 20:
        pwm.start(angle_to_percent(i))
        i = i-1
        print(i)
        time.sleep(0.1)
