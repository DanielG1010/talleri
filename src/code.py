import time
import board
import busio
import digitalio
import adafruit_rfm9x
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_bh1750
from analogio import AnalogIn
from digitalio import DigitalInOut
import machine
from math import atan2, degrees
import adafruit_mpu6050
import adafruit_dht

# Configuración de la radio RFM9x
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM9X_CS)
RESET = digitalio.DigitalInOut(board.RFM9X_RST)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 20
rfm9x.enable_crc = True
rfm9x.ack_retries = 10
rfm9x.ack_delay = 0.2
rfm9x.ack_wait = 1
rfm9x.xmit_timeout = 0.2
rfm9x.node = 23
rfm9x.destination = 50

# Configuración del módulo ADC
adc = machine.ADC(machine.Pin(32))

# Configuración del sensor MPU6050
i2c = board.I2C()
sensor = adafruit_mpu6050.MPU6050(i2c)

# Configuración del sensor DHT22
dht = adafruit_dht.DHT22(board.D2)

# Establece el umbral (threshold) para la lectura analógica
umbral = 1500  # Depende de la señal del sensor

# Inicializa los contadores y variables
contador_10s = 0
over = 0
over_ant = over

# Tiempo en segundos para la duración del conteo y la lectura del sensor (10 segundos en este caso)
duracion_conteo = 10
tiempo_inicial_min = time.time()

# Función para obtener ángulos de inclinación XZ e YZ
def get_inclination(sensor):
    x, y, z = sensor.acceleration
    return vector_2_degrees(x, z), vector_2_degrees(y, z)

# Función para convertir un vector (x, y) en grados
def vector_2_degrees(x, y):
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle

while True:
    # Tiempo inicial para el conteo actual
    tiempo_inicial = time.time()
    
    while (time.time() - tiempo_inicial) < duracion_conteo:
        # Realiza una lectura analógica
        lectura_analogica = adc.read()

        # Compara la lectura con el umbral
        if (lectura_analogica > umbral):
            if over == 0:
                print("El valor supera el umbral.")
                contador_10s += 1  # Aumenta el contador de 10 segundos
                over = 1
        # Se retorna la bandera de over(threshold) a 0         
        else:
            over = 0

        if over != over_ant:       # Se muestra cuando la señal de over(threshold) cambia, para comprobación
            mensaje = "El estado anterior de over era " + str(over_ant) + " y ahora es " + str(over)
            print(mensaje)

        over_ant = over

    # Calcula el conteo aproximado en 1 minuto
    pulso_por_min = contador_10s * 6
    print("Se superó el umbral", contador_10s, "veces en los últimos 10 segundos.")
    print("La cantidad es aprox", pulso_por_min, "pulsos por minuto")

    # Obtiene los ángulos de inclinación XZ e YZ
    angle_xz, angle_yz = get_inclination(sensor)
    print("XZ angle = {:6.2f}deg   YZ angle = {:6.2f}deg".format(angle_xz, angle_yz))

    # Lectura del sensor de calidad del aire
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        print("Temp: {:.1f} *C \t Humedad: {}%".format(temperature, humidity))
        if (temperature >= 24 or temperature <= 18):
            print("Alerta la temperatura del cuarto puede ser peligrosa.")
    except RuntimeError as e:
        print("La lectura del DHT22 falló: ", e.args)

    # Datos de ejemplo (sustituye con tus propios datos)
    data = "{'temperatura': 25.5, 'humedad': 60.0, 'presion': 1013.25, 'pulsos_por_minuto': " + str(
        pulso_por_min) + "}"
    print(data)
    rfm9x.send(bytes(data, "UTF-8"))
    
    time.sleep(0.2)

