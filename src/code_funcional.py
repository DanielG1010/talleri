import time
import board
import busio
import digitalio
import adafruit_rfm9x
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_bh1750
from analogio import AnalogIn
from digitalio import DigitalInOut
speed = 2.4
count_wind_speed = 0
wind_speed = 0
ban = False
tiempoInicio_viento = time.monotonic()
digital_in11 = DigitalInOut(board.D11)
digital_in = DigitalInOut(board.D10)
analog_in = AnalogIn(board.A1)
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.sea_level_pressure = 1013.25
i2c = board.I2C()
sensor = adafruit_bh1750.BH1750(i2c)
count_hora = 0
tiempoInicio = time.monotonic()
i = 1
count_hora = 0
condicion_velocidad = False
condicion_precipitacion = False
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
uart = busio.UART(board.TX, board.RX, baudrate=9600)
def datos_sensores_meteorologicos():
    a = sensores_varios()
    b = sensor_velocidad()
    c = sensor_precipitacion()
    data = (str(a[0]) + '/' + str(a[1]) + '/' + str(a[2]) + '/' + str(a[3]) + '/' + str(a[4]) + '/' + str(a[5]) + '/' + str(b) + '/' + str(c))
    return data
def bucket_tipped_hora():
    global count_hora
    count_hora = count_hora + 1
    print(count_hora)
    time.sleep(1)
def WindDir(value):
    if (value < 0.23 and value > 0.15):   # 0.21
        return 'ESE 112.5'
    elif (value < 0.29 and value > 0.23):   # 0.27
        return "ENE 67.5"
    elif (value < 0.35 and value > 0.29):   # 0.3
        return "E 90"
    elif (value < 0.45 and value > 0.35):   # 0.41
        return "SSE 157.5"
    elif (value < 0.65 and value > 0.55):   # 0.60
        return "SE 135"
    elif (value < 0.85 and value > 0.75):   # 0.79
        return "SSW 202.5"
    elif (value < 0.98 and value > 0.85):   # 0.93
        return "S 180"
    elif (value < 1.35 and value > 1.25):   # 1.31
        return "NNE 22.5"
    elif (value < 1.55 and value > 1.45):   # 1.49
        return "NE 45"
    elif (value < 1.98 and value > 1.85):   # 1.93
        return "WSW 247.5"
    elif (value < 2.08 and value > 1.98):   # 2.03
        return "SW 225"
    elif (value < 2.31 and value > 2.21):   # 2.26
        return "NNW 337.5"
    elif (value < 2.58 and value > 2.48):  # 2.53
        return "N 0"
    elif (value < 2.72 and value > 2.62):  # 2.67
        return "WNW 292.5"
    elif (value < 2.91 and value > 2.81):  # 2.86
        return "NW 315"
    elif (value < 3.00 and value > 3.15):   # 3.05
        return "W 270"
    else:
        return "0"
def condicionTicks_viento(digital):
    if digital == 3.3:
        ban1 = True
        return ban1
    else:
        ban1 = False
        return ban1
def sensor_velocidad():
    global speed
    global count_wind_speed
    global wind_speed
    global ban
    global tiempoInicio_viento
    while ((time.monotonic() - tiempoInicio_viento) < 11):
        if time.monotonic() - tiempoInicio_viento <= 10:
            if ban:
                c = digital_in11.value*3.3
                if (c == 0):
                    count_wind_speed += 1
                    ban = False
            elif not ban:        #Revisar con sensores y el rj11
                c = digital_in11.value*3.3
                ban = condicionTicks_viento(c)
        elif time.monotonic() - tiempoInicio_viento > 10:
            wind_speed = (count_wind_speed * speed)/10
            count_wind_speed = 0
            tiempoInicio_viento = time.monotonic()
            return wind_speed
def sensor_precipitacion():
    global tiempoInicio
    bucket_size = 0.28
    global count_hora
    global i
    while ((time.monotonic() - tiempoInicio) < 51):
        if time.monotonic() - tiempoInicio < 50:
            a = digital_in.value*3.3
            if a == 0:
                bucket_tipped_hora()
        elif time.monotonic() - tiempoInicio >= 50:
            precipitacion_minuto = bucket_size*count_hora
            count_hora = 0
            i += 1
            tiempoInicio = time.monotonic()
            return precipitacion_minuto
def sensores_varios():
    lectura_sensores = [bme280.temperature, bme280.relative_humidity, bme280.pressure,
                        bme280.altitude, sensor.lux, WindDir(analog_in.value*3.3/65536)]
    return lectura_sensores
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
def send_ack(destination):
    rfm9x.destination = destination
    rfm9x.send(b"ok")
def rec_ack():
    packet = rfm9x.receive(
        with_ack=False, with_header=True, timeout=0.1, keep_listening=True
    )
    if packet is not None:
        if packet[4:] == b"ok":
            return True
        else:
            return False
    else:
        return False
while True:
    data = str(datos_sensores_meteorologicos())
    print(data)
    #print("Datos a enviar: {}".format(data))
    rfm9x.send(bytes(data, "UTF-8"))
    ack = rec_ack()
    while not ack:
        print("Acknowledge {}".format(ack))
        rfm9x.send(bytes(data, "UTF-8"))
        ack = rec_ack()
