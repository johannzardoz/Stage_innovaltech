# coding=utf-8

from espeak import espeak
from googletrans import Translator
import RPi.GPIO as GPIO
import time
import random

espeak.set_voice("en")

ouverte = 20
ferme = 60

GPIO.setmode(GPIO.BOARD) #Use Board numerotation mode
GPIO.setwarnings(False) #Disable warnings

def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180 #Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent

#Use pin 37 for PWM signal
pwm_gpio = 29
frequence = 50
GPIO.setup(pwm_gpio, GPIO.OUT)
pwm = GPIO.PWM(pwm_gpio, frequence)
pwm.start(angle_to_percent(0))

voyelles = ['a','e','i','o','u','y','é','è','ê','à','ô','î','â','û']
consonnes = ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','z','ç']

def decoupage_syllabes(text):
    texte_par_syllabes = 0
    for i in range(0,len(text)-1):
        if text[i] in consonnes and text[i-1] in voyelles or text[i] == ' ':
            texte_par_syllabes = texte_par_syllabes + 1
    return texte_par_syllabes

def mouvement_bouche(nombre_syllabes):
    for i in range(nombre_syllabes):
        
        pwm.ChangeDutyCycle(angle_to_percent(ouverte))
        time.sleep(0.1)
        pwm.ChangeDutyCycle(angle_to_percent(ferme))
        time.sleep(0.1)

trans= Translator()
text =  "Je suis le robot bilbot"
translation = trans.translate(text, src='fr', dest='en')

texte_traduit = translation.text
espeak.synth(texte_traduit)

mouvement_bouche(decoupage_syllabes(translation.text))
pwm.ChangeDutyCycle(angle_to_percent(ferme))
time.sleep(1)

pwm.stop()
GPIO.cleanup()