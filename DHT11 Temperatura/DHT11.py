import time

import adafruit_dht
import board

dht = adafruit_dht.DHT22(board.D2)

while True:
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        print("Temp: {:.1f} *C \t Humedad: {}%".format(temperature, humidity))
        if(temperature >= 24 or temperature <= 18)
            print("Alerta la temperatura del cuarto puede ser peligrosa.")
    except RuntimeError as e:
        print("La lectura del DHT11 falló: ", e.args)

    time.sleep(1)
