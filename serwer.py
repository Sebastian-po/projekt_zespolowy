import time
import network
import socket


ssid = 'nazwa_sieci'
password = 'haslo'


html = """<!DOCTYPE html>
<html>
<head> <title>Wroclaw Dynamics</title> </head>
<body> 
<p>Hello, Wroclaw Dynamics!</p>
</body>
</html>
"""
def start_http_server():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
    
# Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('Connected')
        status = wlan.ifconfig()
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        print('Server URL: http://%s:%d' % (status[0], addr[1]))
        
        
    # Open socket
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('listening on', addr)
    while True:
        try:       
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            response = html
            cl.send(response)
            cl.close()
     
        except OSError as e:
            cl.close()
            print('connection closed')
            
            
start_http_server()