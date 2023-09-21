import time
import board
import busio
import digitalio
import adafruit_rfm9x
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_bh1750
from analogio import AnalogIn
from digitalio import DigitalInOut
from adafruit_bus_device.i2c_device import I2CDevice
import adafruit_character_lcd.character_lcd_i2c as character_lcd

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

# Función para enviar un ACK (acknowledge)
def send_ack(destination):
    rfm9x.destination = destination
    rfm9x.send(b"ok")

# Función para recibir un ACK (acknowledge)
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

# Función para obtener datos de sensores meteorológicos (debes completar esta función)

# Configuración del sensor de calidad del aire
buzzerPin = digitalio.DigitalInOut(board.D10)
buzzerPin.direction = digitalio.Direction.OUTPUT

greenLED = digitalio.DigitalInOut(board.D11)
greenLED.direction = digitalio.Direction.OUTPUT

redLED = digitalio.DigitalInOut(board.D12)
redLED.direction = digitalio.Direction.OUTPUT

sensorPin = analogio.AnalogIn(board.A5)

# Configuración del LCD de caracteres
lcd_columns = 16
lcd_rows = 2

i2c = board.I2C()  # usa board.SCL y board.SDA
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows)

feather_address = 0x00  # Reemplaza esto con la dirección I2C de tu Feather
feather_device = I2CDevice(i2c, feather_address)
lcd.backlight = True

while True:

    recibidos = rfm9x.receive(with_ack = True)
    # Lectura del sensor de calidad del aire
    sensorValue = sensorPin.value
    print("AirQuality Value: ", sensorValue)

    if sensorValue > 600:
        greenLED.value = False
        buzzerPin.value = True
        redLED.value = True
        print("Alert!!!")
        time.sleep(2)
    else:
        greenLED.value = True
        redLED.value = False
        buzzerPin.value = False
        print("Normal")
        time.sleep(0.5)

    # Lectura de datos enviados por el Feather al LCD
    with feather_device:
        data = bytearray(32)
        feather_device.readinto(data)
        message = data.decode('utf-8').strip('\x00')
        lcd.message = message
    
    time.sleep(0.1)

