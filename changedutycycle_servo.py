import RPi.GPIO as GPIO
import time

servoPIN = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) # Initialization

while True:
    p.ChangeDutyCycle(6.5)
    time.sleep(0.01)
    p.ChangeDutyCycle(0)
    time.sleep(0.01)