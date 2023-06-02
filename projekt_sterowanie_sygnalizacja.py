import machine
import time
import uasyncio
import network
import socket
from machine import Pin, PWM

led1 = PIN(2, Pin.OUT)
led2 = PIN(3, Pin,OUT)

adc = machine.ADC(0)
pin_pompy = Pin(22, Pin.OUT)

#GPIO17 do sterowania serwem
servo = PWM(Pin(17))

#Czestotliwosc dla PWM = 50Hz (20msec)
servo.freq(50)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
prog_wilgotnosci = 40

#Ustalenie prędkości obrotu serwomechanizmu
#zgodnie z obrotem zegara
ServoForward = 1450000

#Zatrzymanie serwomechanizmu
ServoStop = 1485000

#Ustalenie prędkości obrotu serwomechanizmu
#przeciwnie z obrotem zegara
ServoReverse = 1505000

ssid = 'ssid'
password = 'password'

html_template = """
<!DOCTYPE html>
<html>
    <head>
        <title>Wroclaw Dynamics</title>
    </head>
    <body> 
        <p>Wilgotnosc gleby: {wilgotnosc} %</p>
    </body>
</html>
"""

# Odczyt poziomy wilgotności z czujnika
async def odczyt_wilgotnosci(adc):
    odczyt = adc.read_u16()
    procent = int((odczyt / 65535) * 100)
    wilgotnosc = 100 - procent
    return wilgotnosc

# Pętla główna czujnika wilgoci oraz pompy wody
async def sterowanie(adc, led1, pin_pompy, prog_wilgotnosci):
    while True:
        wilgotnosc = await odczyt_wilgotnosci(adc)
        print("Wartość odczytu wilgotności: %.2f procent" % wilgotnosc)
        # Sprawdzenie, czy wartość wilgotności jest większa od progu
        if wilgotnosc > prog_wilgotnosci:
            # Włączenie pompy wodnej na 5 sekund
            pin_pompy.value(1)
            await uasyncio.sleep_ms(5000)
            pin_pompy.value(0)
        
        await uasyncio.sleep_ms(10000)

# Pętla główna sterowania obrotami serwomechanizmu
async def rotation(servo,ServoForward,ServoStop,ServoReverse):
    while True:
        #obrót o 360 stopni zgodnie z ruchem wskazówek zegara, obrót o jeden stopień co 4 minuty
        for i in range(0,360):
            servo.duty_ns(ServoForward)
            await uasyncio.sleep_ms(25)
            servo.duty_ns(ServoStop)
            await uasyncio.sleep_ms(240000)
            time.sleep(1)

        #obrót o 360 stopni przeciwnie do ruchu wskazówek zegara, obrót o jeden stopień co 4 minuty
        for j in range(0,360):
            servo.duty_ns(ServoReverse)
            await uasyncio.sleep_ms(25)
            servo.duty_ns(ServoStop)
            await uasyncio.sleep_ms(240000)
    
# Pętla główna serwera http
async def start_http_server(addr, adc, led2, pin_pompy, prog_wilgotnosci):
    while True:
        wlan = network.WLAN(network.STA_IF)
    	wlan.active(True)
    	wlan.connect(ssid, password)
    	max_wait = 10

    	while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                 break
            max_wait -= 1
            
            print('waiting for connection...')
                
            led2.value(not led2.value())
            await uasyncio.sleep(1)
     
        if wlan.status() != 3:
            raise RuntimeError('network connection failed')
        else:
            print('Connected')
            led2.value(1)
            status = wlan.ifconfig()
            print('Server URL: http://%s:%d' % (status[0], addr[1]))

        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        print('listening on', addr)

        while True:
            try:
                cl, addr = s.accept()
                print('client connected from', addr)
                request = cl.recv(1024)

                wilgotnosc = await odczyt_wilgotnosci(adc)
                html = html_template.format(wilgotnosc=wilgotnosc)
                cl.send(html)
                cl.close()
            except OSError as e:
                cl.close()
                print('connection closed')
        led2.value(0)
        await uasyncio.sleep_ms(10000)
        

async def main():
    led1.value(1)
    try:
        while True:
            tasks = []
            tasks.append(uasyncio.create_task(start_http_server(addr, adc, led2, pin_pompy, prog_wilgotnosci)))
            tasks.append(uasyncio.create_task(sterowanie(adc, led1, pin_pompy, prog_wilgotnosci)))
            tasks.append(uasyncio.create_task(rotation(servo,ServoForward,ServoStop,ServoReverse)))
            await uasyncio.gather(*tasks)
            
    finally:
        led1.value(0)
        
if __name__ == "__main__":
    uasyncio.run(main())