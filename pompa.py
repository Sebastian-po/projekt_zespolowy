from machine import Pin
import time

# Ustawienie pinu GP22 (numer 29) jako wyjście
pump_pin = Pin(22, Pin.OUT)

# Pętla włączająca i wyłączająca pompę
while True:

        print("Pump on")
        pump_pin.on()         
        time.sleep(5)
        pump_pin.off()         # Wyłączenie pompy
        print("Pump off")      # Wyświetlenie stanu pompy
        time.sleep(5)              # Poczekaj 5 sekund