import pyttsx3
from googletrans import Translator

def mouvement_bouche():
    

engine = pyttsx3.init()

# réglage de la voix en français
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[20].id)

trans= Translator()
text =  "bonjour je m'appelle Johann"
translation = trans.translate(text, src='fr', dest='en')
print(translation.text)
engine.say(translation.text)
engine.runAndWait()