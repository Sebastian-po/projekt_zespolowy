from machine import Pin, PWM
import time

#GPIO17 do sterowania serwem
servo = PWM(Pin(17))
#Czestotliwosc dla PWM = 50Hz (20msec)
servo.freq(50)

#Ustalenie prędkości obrotu serwomechanizmu
#zgodnie z obrotem zegara
ServoForward = 1450000
#Zatrzymanie serwomechanizmu
ServoStop = 1485000
#Ustalenie prędkości obrotu serwomechanizmu
#przeciwnie z obrotem zegara
ServoReverse = 1505000


def rotation():
    #obrót o 360 stopnii, obrót o jeden stopień co 4 minuty
    for i in range(0,360):
        servo.duty_ns(ServoForward)
        time.sleep(0.025)
        servo.duty_ns(ServoStop)
        time.sleep(240)
    #obrót o 360 stopnii w drugą stronę, obrót o jeden stopień co 4 minuty
    for j in range(0,360):
        servo.duty_ns(ServoReverse)
        time.sleep(0.025)
        servo.duty_ns(ServoStop)
        time.sleep(240)

     
