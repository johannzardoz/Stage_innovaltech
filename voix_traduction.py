# coding=utf-8
from espeak import espeak
from googletrans import Translator
import RPi.GPIO as GPIO
import time
import os
import random
import urllib.request

import pygame
import pygame_menu

#valeurs d'angle d'ouverture et de fermeture de la bouce
ouverte = 20
ferme = 60

GPIO.setmode(GPIO.BOARD) #Utilisation de la numérotation board du GPIO
GPIO.setwarnings(False) #Desactivation des avertissements liés au GPIO

#Fonction convertissant un angle en impulsion pour le servomoteur
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180

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

#La liste des langues disponibles
liste_langues = ['fr','en','pt','de','es']
#Parametres par defaults de la traduction
langue_texte = 'fr'
langue_traduction = 'fr'
vitesse_choisie = '150'
type_vitesse = 'rapide'
volume = '300'

#Fonction permettant de verifier si la raspberry est connectee a internet
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False

#Fonction affilié au bouton de choix de la vitesse de l'interface
def interface_choix_vitesse(a,b):
    global vitesse_choisie
    global type_vitesse
    if b == 0:
        vitesse_choisie = '150'
        type_vitesse = 'rapide'
    if b == 1:
        vitesse_choisie = '20'
        type_vitesse = 'lent'

#Fonction affilié au bouton de choix du volume de l'interface
def interface_volume(a):
    global volume
    volume = a
    print(volume)

#Fonction affilié au bouton de choix de la langue d'entree de l'interface
def interface_langue_texte(a,b):
    global langue_texte
    langue_texte = liste_langues[b]
    print(langue_texte)

#Fonction affilié au bouton de choix de la langue de sortie de l'interface
def interface_langue_traduction(a,b):
    global langue_traduction
    langue_traduction = liste_langues[b]
    print(langue_traduction)

#Fonction affilié au bouton de choix du texte de l'interface
def interface_texte(a):
    global text
    text = a
    print(text)

#Fonction s'executant quand l'utilisateur clique sur le bouton lancant la traduction
def interface_traduction():
    global text
    
    #si la langue d'entree n'est pas la meme que celle de sortie = necessite traduction
    if langue_texte != langue_traduction:
        
        #verification si la raspberry est connectée a internet
        if connect() == True:
            
            #declaration du traducteur
            trans= Translator()
            translation = trans.translate(text, src=langue_texte, dest=langue_traduction)
            #traduction du texte
            texte_traduit = translation.text
            print(texte_traduit)
            
            #decoupage mot par mot du texte
            parole = texte_traduit.split(' ')
            for i in parole:
                #ouverture de la bouche
                pwm.ChangeDutyCycle(angle_to_percent(ouverte))
                #lecture du mot en fonction de la vitesse choisie par l'utilisateur
                if type_vitesse == 'rapide':
                    os.system('espeak -s '+vitesse_choisie+' -a '+volume+' -z -v '+langue_traduction+' "'+i+'"')
                if type_vitesse == 'lent':
                    os.system('espeak -s '+vitesse_choisie+' -a '+volume+' -v '+langue_traduction+' "'+i+'"')
                #fermeture de la bouche
                pwm.ChangeDutyCycle(angle_to_percent(ferme))
                time.sleep(0.05)
        
        #si pas de connexion internet
        else:
            text = "pas de connection internet, traduction impossible"
            #decoupage mot par mot du texte
            parole = text.split(' ')
            
            for i in parole:
                #ouverture de la bouche
                pwm.ChangeDutyCycle(angle_to_percent(ouverte))
                #lecture mot par mot de la phrase
                os.system('espeak -s 150 -a '+volume+' -z -v fr "'+i+'"')
                #fermeture de la bouche
                pwm.ChangeDutyCycle(angle_to_percent(ferme))
                time.sleep(0.05)
    
    #si la langue de destination est la meme que celle d'entree : pas besoin de traduction
    if langue_texte == langue_traduction:
    
       #decoupage mot par mot du texte
       parole = text.split(' ')
       for i in parole:
            #ouverture de la bouche
            pwm.ChangeDutyCycle(angle_to_percent(ouverte))
            #lecture du mot en fonction de la vitesse choisie par l'utilisateur
            if type_vitesse == 'rapide':
                os.system('espeak -s '+vitesse_choisie+' -a '+volume+' -z -v '+langue_traduction+' "'+i+'"')
            if type_vitesse == 'lent':
                os.system('espeak -s '+vitesse_choisie+' -a '+volume+' -v '+langue_traduction+' "'+i+'"')
            #fermeture de la bouche
            pwm.ChangeDutyCycle(angle_to_percent(ferme))
            time.sleep(0.05)
    
    #fermeture de la bouche
    pwm.ChangeDutyCycle(angle_to_percent(ferme))
    time.sleep(1)
    pwm.ChangeDutyCycle(0)

#creation de l'interface
    
#initialisation de pygame
pygame.init()
#dimensiosn du menu
surface = pygame.display.set_mode((1500, 600))
#creation du menu
menu = pygame_menu.Menu(600, 1500, 'BILBOT LE TRADUCTEUR',theme=pygame_menu.themes.THEME_DARK)

#ajout de tous les boutons, selecteurs et text input du menu
menu.add.selector('Vitesse de parole : ', [('Rapide', 0), ('Lente', 1)], onchange=interface_choix_vitesse)
menu.add.text_input('Volume : ', default='300', onreturn=interface_volume)
menu.add.selector('Langue du texte à traduire : ', [('Français', 0), ('Anglais', 1), ('Portugais', 2), ('Allemand', 3), ('Espagnol', 4)], onchange=interface_langue_texte)
menu.add.selector('Langue dans laquelle traduire : ', [('Français', 0), ('Anglais', 1), ('Portugais', 2), ('Allemand', 3), ('Espagnol', 4)], onchange=interface_langue_traduction)
menu.add.text_input('Texte à traduire : ', default='', onreturn=interface_texte)
menu.add.button('Lecture du texte par BilBot', interface_traduction)
menu.add.button('Quitter', pygame_menu.events.EXIT)
#mise en fonctionnement du menu
menu.mainloop(surface)