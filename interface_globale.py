# coding=utf-8
#Pour la voix
from espeak import espeak
from googletrans import Translator
import urllib.request

#Gestion des E/S (servos, led)
import RPi.GPIO as GPIO

#Pour scanner un QR code
import pyzbar.pyzbar as pyzbar

#Pour generer l'interface
import pygame
import pygame_menu

#Traitement d'image
import cv2
import numpy as np
import imutils

import time
import os

##########################################
#########DECLARATION DES VARIABLES########
##########################################

#Valeurs d'angles limites des servos
hauteur_max_yeux = 90
hauteur_min_yeux = 70
hauteur_moyennes_yeux = 80

gauche_max_yeux = 80
droite_max_yeux = 25
centre_x_yeux = 55

bouche_fermee = 60
bouche_ouverte = 20

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

    #Allumage de la LED
    GPIO.output(led_broche, GPIO.HIGH)
    GPIO.output(led_socle, GPIO.HIGH)

##########################################
############TRADUCTION DE TEXTE###########
##########################################

def traduction_de_texte():
    
    #Valeurs d'angles limites des servos
    hauteur_max_yeux = 90
    hauteur_min_yeux = 70
    hauteur_moyennes_yeux = 80

    gauche_max_yeux = 80
    droite_max_yeux = 25
    centre_x_yeux = 55

    bouche_fermee = 60
    bouche_ouverte = 20
    
    #Liste des langues disponibles
    liste_langues = ['fr','en','pt','de','es']

    #Parametres par defaults de la traduction
    global langue_texte
    global langue_traduction
    global vitesse_choisie
    global type_vitesse
    global volume
    
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
                    servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
                    #lecture du mot en fonction de la vitesse choisie par l'utilisateur
                    if type_vitesse == 'rapide':
                        os.system('espeak -s '+vitesse_choisie+' -a '+volume+' -z -v '+langue_traduction+' "'+i+'"')
                    if type_vitesse == 'lent':
                        os.system('espeak -s '+vitesse_choisie+' -a '+volume+' -v '+langue_traduction+' "'+i+'"')
                    #fermeture de la bouche
                    servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
                    time.sleep(0.05)
            
            #si pas de connexion internet
            else:
                text = "pas de connection internet, traduction impossible"
                #decoupage mot par mot du texte
                parole = text.split(' ')
                
                for i in parole:
                    #ouverture de la bouche
                    servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
                    #lecture mot par mot de la phrase
                    os.system('espeak -s 150 -a '+volume+' -z -v fr "'+i+'"')
                    #fermeture de la bouche
                    servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
                    time.sleep(0.05)
        
        #si la langue de destination est la meme que celle d'entree : pas besoin de traduction
        if langue_texte == langue_traduction:
        
           #decoupage mot par mot du texte
           parole = text.split(' ')
           for i in parole:
                #ouverture de la bouche
                servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
                #lecture du mot en fonction de la vitesse choisie par l'utilisateur
                if type_vitesse == 'rapide':
                    os.system('espeak -s '+vitesse_choisie+' -a '+volume+' -z -v '+langue_traduction+' "'+i+'"')
                if type_vitesse == 'lent':
                    os.system('espeak -s '+vitesse_choisie+' -a '+volume+' -v '+langue_traduction+' "'+i+'"')
                #fermeture de la bouche
                servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
                time.sleep(0.05)
        
        #fermeture de la bouche
        servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
        time.sleep(1)
        servo_bouche.ChangeDutyCycle(0)

    #creation de l'interface
        
    #dimensiosn du menu
    surface = pygame.display.set_mode((1500, 800))
    #creation du menu
    menu = pygame_menu.Menu(800, 1500, 'BILBOT LE TRADUCTEUR',theme=pygame_menu.themes.THEME_DARK)

    #ajout de tous les boutons, selecteurs et text input du menu
    menu.add.selector('Vitesse de parole : ', [('Rapide', 0), ('Lente', 1)], onchange=interface_choix_vitesse)
    menu.add.text_input('Volume : ', default='300', onreturn=interface_volume)
    menu.add.selector('Langue du texte à traduire : ', [('Français', 0), ('Anglais', 1), ('Portugais', 2), ('Allemand', 3), ('Espagnol', 4)], onchange=interface_langue_texte)
    menu.add.selector('Langue dans laquelle traduire : ', [('Français', 0), ('Anglais', 1), ('Portugais', 2), ('Allemand', 3), ('Espagnol', 4)], onchange=interface_langue_traduction)
    menu.add.text_input('Texte à traduire : ', default='', onreturn=interface_texte)
    menu.add.button('Lecture du texte par BilBot', interface_traduction)
    menu.add.button('Retour au menu', choix_programme)
    #mise en fonctionnement du menu
    menu.mainloop(surface)

##########################################
############LECTURE DE QR CODE############
##########################################
    
def lecture_de_qr_code():
    
    #Valeurs d'angles limites des servos
    hauteur_max_yeux = 90
    hauteur_min_yeux = 70
    hauteur_moyennes_yeux = 80

    gauche_max_yeux = 80
    droite_max_yeux = 25
    centre_x_yeux = 55

    bouche_fermee = 60
    bouche_ouverte = 20
    
    #intervalle de temps entre 2 lecture du meme QR code
    intervale_QR = 8
    
    #Parametres de la voix de base
    vitesse = '150'
    volume = '300'
    langue = 'fr'
    
    #Initialisation de l'ancien data (permettant de ne pas lire 2 fois a la suite le meme QR code
    old_data = ''
    
    #Capture video
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_PLAIN
    
    while True:
        #Eteignage du servo de la bouche (pour limiter la nuisance sonore
        servo_bouche.ChangeDutyCycle(0)
        #Recuperation de l'image
        _, frame = cap.read()
        #Detection des QR codes sur l'image
        decodedObjects = pyzbar.decode(frame)
        for obj in decodedObjects:
            #Prise du temps
            actual_time = time.time()
            #Recuperation du texte
            data = obj.data
            #Conversion du message en byte en string
            data = data.decode('UTF-8')
            #Affichage du texte du QR code sur l'image
            cv2.putText(frame, str(data), (50, 50), font, 2,(255, 0, 0), 3)
            
            #On verifie que soit le QR code n'est pas le meme que l'ancien, soit l'intervalle de temps est passee
            if data != old_data or start_time + intervale_QR < actual_time :
                #L'ancien QR code devient le nouveau
                old_data = data
                #Reset du temps
                start_time = time.time()
                #Coupage du texte du QR code en mot par mot
                data_spit = data.split(' ')
                for i in data_spit:
                    #ouverture de la bouche
                    servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
                    #Lecture du mot
                    os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
                    #fermeture de la bouche
                    servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
                    time.sleep(0.05)
        
        #Affichage de l'image
        cv2.imshow("affichage",frame)
        
        #Si l'utilisateur appui sur echap le programme se coupe
        k = cv2.waitKey(5)
        if k == 27:
            break

    #Destruction des fenetres
    cv2.destroyAllWindows()

##########################################
############SUIVEUR DE VISAGE#############
##########################################
    
def suiveur_de_visage():
    
    #Valeurs d'angles limites des servos
    hauteur_max_yeux = 90
    hauteur_min_yeux = 70
    hauteur_moyennes_yeux = 80

    gauche_max_yeux = 80
    droite_max_yeux = 25
    centre_x_yeux = 55

    bouche_fermee = 60
    bouche_ouverte = 20
    
    #intervalle de temps entre 2 comptage de visages
    intervale_visage = 8
    
    #Angles modifies pour le deplacement des yeux
    angle_x = centre_x_yeux
    angle_y = hauteur_moyennes_yeux
    
    #Dimensions de la fenetre OpenCV
    largueur = 640
    hauteur = 480
    
    #Precision du suiveur avec la camera
    precision = 80
    
    #Capture video
    video_capture = cv2.VideoCapture(0)
    
    #Classifier utilise pour la detection de visages
    cascPath = "/home/pi/Desktop/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)

    while True:
        #Retour video
        ret, frame = video_capture.read()
        #Redimensionnement de l'image
        resized = cv2.resize(frame, (largueur, hauteur))
        #Changement de l'image en nuances de gris
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        #Detection des visages
        faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(60, 60),flags=cv2.CASCADE_SCALE_IMAGE)
        #Pour chaque visage detecte
        for (x,y,w,h) in faces:
            #Affichage d'un cadre autour du visage
            cv2.rectangle(resized, (x, y), (x + w, y + h),(0,255,0), 2)
            
            #Determination de la direction dans laquelle faire tourner les servos pour suivre le visage
            if x > (largueur+precision)/2:
                     #print('droite')
                     #print(cx)
                     angle_x = angle_x - 1
                     
                     if angle_x < droite_max_yeux:
                        angle_x = droite_max_yeux
                     #print(angle)
                
            if x < (largueur-precision)/2:
                     #print('gauche')
                     #print(cx)
                     angle_x = angle_x + 1
                    
                     if angle_x > gauche_max_yeux:
                        angle_x = gauche_max_yeux
                     #print(angle)
                
            if y > (hauteur+precision)/2:
                     #print('droite')
                     #print(cx)
                     angle_y = angle_y - 1
                     
                     if angle_y < hauteur_min_yeux:
                        angle_y = hauteur_min_yeux
                     #print(angle)
                
            if y < (hauteur-precision)/2:
                     #print('gauche')
                     #print(cx)
                     angle_y = angle_y + 1
                    
                     if angle_y > hauteur_max_yeux:
                        angle_y = hauteur_max_yeux
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

##########################################
########SUIVEUR DE BOITE RASPBERRY########
##########################################
    
def suiveur_de_boite_raspberry():
    
    #Valeurs d'angles limites des servos
    hauteur_max_yeux = 90
    hauteur_min_yeux = 70
    hauteur_moyennes_yeux = 80

    gauche_max_yeux = 80
    droite_max_yeux = 25
    centre_x_yeux = 55

    bouche_fermee = 60
    bouche_ouverte = 20
    
    #Angles modifies pour le deplacement des yeux
    angle_x = centre_x_yeux
    angle_y = hauteur_moyennes_yeux
    
    #Dimensions de la fenetre OpenCV
    largueur = 640
    hauteur = 480
    
    #Precision du suiveur avec la camera
    precision = 80
    
    #Capture video
    video_capture = cv2.VideoCapture(0)
    
    while True:
         #Retour video
         _,frame= video_capture.read()
         #Redimensionnement de l'image
         resized = cv2.resize(frame, (largueur, hauteur))
         #Modification des couleurs de l'image en HSV
         hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        
         #Bornes du rouge d'une boite Raspberry
         lower_red = np.array([140,170,70])
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

##########################################
###########COMPTEUR DE PERSONNES##########
##########################################
    
def compteur_de_personnes():
    
    #Valeurs d'angles limites des servos
    hauteur_max_yeux = 90
    hauteur_min_yeux = 70
    hauteur_moyennes_yeux = 80

    gauche_max_yeux = 80
    droite_max_yeux = 25
    centre_x_yeux = 55

    bouche_fermee = 60
    bouche_ouverte = 20
    
    #Parametres de la voix de base
    vitesse = '150'
    volume = '300'
    langue = 'fr'
    
    #Classifier utilise pour la detection de visages
    cascPath = "/home/pi/Desktop/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascPath)
    
    #Intervalle entre la detection des personnes
    intervale_visage = 8
    
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
        
        
        if actual_time > start_time + intervale_visage:
            text = "je vois "+str(len(faces))+" personnes"
            print(text)
            text_coupe = text.split(' ')
            
            for i in text_coupe:
                #ouverture de la bouche
                servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
                os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
                #fermeture de la bouche
                servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
                time.sleep(0.05)
            
            servo_bouche.ChangeDutyCycle(0)
            start_time = time.time()
            
        cv2.imshow('Video', frame)
        
        k = cv2.waitKey(5)
        if k == 27:
             break
        
    cv2.destroyAllWindows()

##########################################
############CHOIX DU PROGRAMMME###########
##########################################

def choix_programme():
    #initialisation de pygame
    pygame.init()
    #dimensiosn du menu
    surface = pygame.display.set_mode((1500, 800))
    #creation du menu
    choix_programme = pygame_menu.Menu(800, 1500, 'BILBOT',theme=pygame_menu.themes.THEME_DARK)
    
    choix_programme.add.label('****************************')
    choix_programme.add.button('TRADUCTION DE TEXTE', traduction_de_texte)
    choix_programme.add.button('LECTURE DE QR CODE', lecture_de_qr_code)
    choix_programme.add.button('SUIVEUR DE VISAGE', suiveur_de_visage)
    choix_programme.add.button('SUIVEUR DE BOITE RASPBERRY', suiveur_de_boite_raspberry)
    choix_programme.add.button('COMPTEUR DE PERSONNES', compteur_de_personnes)
    choix_programme.add.button('REGARD AU CENTRE', regard_au_centre)
    choix_programme.add.label('****************************')
    choix_programme.add.button('QUITTER', pygame_menu.events.EXIT)

    #mise en fonctionnement du menu
    choix_programme.mainloop(surface)

regard_au_centre()
choix_programme()