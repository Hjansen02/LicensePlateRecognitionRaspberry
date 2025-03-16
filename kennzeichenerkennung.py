import pandas as pd
import cv2
import time
import RPi.GPIO as GPIO
from openalpr import Alpr
import tkinter as tk
from tkinter import messagebox
import sys

GPIO.setmode(GPIO.BCM)
LED_PIN=47
GPIO.setup(LED_PIN, GPIO.OUT)

dauer_global = 25

def lade_tabelle():
    tb = pd.read_excel(Pfad)  #Path to the plate table !!!!!!
    return tb["Kennzeichen"].tolist()

def open_door():
    GPIO.output(18, True)
    time.sleep(dauer_global)
    GPIO.output(18, False)
    
def blink_led():
    end_time = time.time() + time_global
    while time.time() < end_time:
        GPIO.output(LED_PIN, True)
        time.sleep(0.5)
        GPIO.output(LED_PIN, False)
        time.sleep(0.5)
    
    
def process_frame(frame):
    cv2.imwrite('temp.jpg', frame)
    results = alpr.recognize_file('temp.jpg')
    
    for plate in results['results']:
        print("Plate Recognised:", plate['plate'])
        if plate['plate'] in allowed_plates:
           open_door()
           blink_led()

def start_recognition():
    global cap, running
    running = True
    cap = cv2.VideoCapture(0)
    while running:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Kennzeichen', frame)
            process_frame(frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()

def stop_recognition():
    global running
    running = False

def manual_open():
    GPIO.output(18, True)
    GPIO.output(LED_PIN, True)
def manual_close():
    GPIO.output(18, False)
    GPIO.output(LED_PIN, False)
    
def set_duration(value):
    global time_global
    time_global = int(value)
    messagebox.showinfo("Info", f"Time opened set to: {time_global}.")

alpr = Alpr("eu", "/path/to/openalpr.conf", "/path/to/runtime_data")
if not alpr.is_loaded():
    print("Fehler beim Laden von OpenALPR")
    sys.exit(1)

alpr.set_top_n(20)
alpr.set_default_region("de")

allowed_plates = lade_tabelle()

#Erstelle das Hauptfenster
root = tk.Tk()
root.title("Kennzeichenerkennung")

button_start = tk.Button(root, text="Erkennung starten", command=start_recognition)
button_start.pack(pady=5)

button_stop = tk.Button(root, text="Erkennung stoppen", command=stop_recognition)
button_stop.pack(pady=5)

button_open = tk.Button(root, text="Tor öffnen", command=manual_open)
button_open.pack(pady=5)

button_close = tk.Button(root, text="Tor schließen", command=manual_close)
button_close.pack(pady=5)

scale_dauer = tk.Scale(root, from_=5, to=60, orient="horizontal", label="Dauer (Sekunden)", command=set_duration)
scale_dauer.set(dauer_global)
scale_dauer.pack(pady=5)

root.mainloop()
GPIO.cleanup()
