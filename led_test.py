import RPi.GPIO as GPIO
import time

led_broche = 37
led_socle = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(led_broche, GPIO.OUT)
GPIO.setup(led_socle, GPIO.OUT)
p = GPIO.PWM(led_broche, 50)
p2 = GPIO.PWM(led_socle, 50)

#while True:
    #for i in range (0,100):
    #    print(i)
    #    p.start(i)
    #    time.sleep(0.05)
    #for i in range (0,100):
    #    print(i)
    #    p.start(100-i)
    #    time.sleep(0.05)
    
p.start(0)
p2.start(0)
