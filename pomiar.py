import time
from machine import Pin
import uasyncio
 
adc = machine.ADC(0)
pin_pompy = Pin(22, Pin.OUT)
prog_wilgotnosci = 40


async def sterowanie():
    # Odczyt wartości wilgotności gleby z czujnika
    odczyt = adc.read_u16()

    # Przeliczenie wartości odczytanej z przetwornika ADC na wartość procentową
    procent = int((odczyt / 65535) * 100)
    wilgotnosc = 100 - procent
    print("Wartość odczytu wilgotności: %.2f procent" % wilgotnosc)
    # Sprawdzenie, czy wartość wilgotności jest większa od progu
    if wilgotnosc > prog_wilgotnosci:
    # Włączenie pompy wodnej na 5 sekund
        pin_pompy.value(1)
        await uasyncio.sleep_ms(5000)
        pin_pompy.value(0)
    
async def main():
    while True:
        uasyncio.create_task(sterowanie())
        await uasyncio.sleep_ms(10000)
    
uasyncio.run(main())


#wyzsza wartosc odczytu mniejsza wilgotnosc