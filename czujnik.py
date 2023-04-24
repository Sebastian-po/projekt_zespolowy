import machine
import time

# Ustawienie wskazanej liczby bitów ADC (domyślnie 12)
adc = machine.ADC(0)

while True:
    # Odczytaj wartość napięcia z portu ADC
    val = adc.read_u16()

     # Konwersja wartości z zakresu 0-65535 na napięcie w mV
    percent = (val * 3 / 65535 )*100/3

    # Wyświetlenie wartości napięcia na konsoli
    print("Wartość napięcia: %.2f mV" % percent)
    # Poczekaj 1 sekundę przed kolejnym odczytem
    time.sleep(1)
