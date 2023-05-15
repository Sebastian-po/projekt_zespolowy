import time
import network
import socket
import uasyncio
import machine

ssid = 'ssid'
password = 'password'

html_template = """<!DOCTYPE html>
<html>
<head> <title>Wroclaw Dynamics</title>
</head>
<body> 
<p>Wilgotnosc gleby: {wilgotnosc} %</p>
</body>
</html>
"""

async def odczyt_wilgotnosci(adc):
    odczyt = adc.read_u16()
    procent = int((odczyt / 65535) * 100)
    wilgotnosc = 100 - procent
    return wilgotnosc

async def sterowanie(adc, pin_pompy, prog_wilgotnosci):
    wilgotnosc = await odczyt_wilgotnosci(adc)
    print("Wartość odczytu wilgotności: %.2f procent" % wilgotnosc)
    if wilgotnosc < prog_wilgotnosci:
        pin_pompy.value(1)
        await uasyncio.sleep_ms(5000)
        pin_pompy.value(0)

async def start_http_server(addr, adc, pin_pompy, prog_wilgotnosci):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        await uasyncio.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('Connected')
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

async def main():
    
    adc = machine.ADC(0)
    pin_pompy = machine.Pin(22, machine.Pin.OUT)
    prog_wilgotnosci = 40
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    
    
    while True:
        tasks = []
        tasks.append(uasyncio.create_task(start_http_server(addr, adc, pin_pompy, prog_wilgotnosci)))
        tasks.append(uasyncio.create_task(sterowanie(adc, pin_pompy, prog_wilgotnosci)))

        await uasyncio.gather(*tasks)
        await uasyncio.sleep_ms(10000)

uasyncio.run(main())
