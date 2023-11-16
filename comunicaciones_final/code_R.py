

import board
import busio
import digitalio
import analogio
import time
from math import atan2, degrees
#import adafruit_mpu6050
import adafruit_rfm9x
import adafruit_dht
import hd44780
#from adafruit_bme280 import basic as adafruit_bme280

RADIO_FREQ_MHZ = 915.0
TIEMPO_ENVIO = 5
CS = digitalio.DigitalInOut(board.RFM9X_CS)
RESET = digitalio.DigitalInOut(board.RFM9X_RST)
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23
mq135 = digitalio.DigitalInOut(board.D6)
mq135.direction = digitalio.Direction.INPUT

#DISPLAY
# Crea la conexión I2C
i2c = busio.I2C(board.SCL, board.SDA)
# Crea la instancia del display
lcd = hd44780.HD44780(i2c, address=0x27)

# Create sensor object, using the board's default I2C bus.
#i2c = board.I2C()   # uses board.SCL and board.SDA
#bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
#bme280.sea_level_pressure = 1013.25

#BUZZER
# Configura el pin para el buzzer
buzzer = digitalio.DigitalInOut(board.D12)  # Reemplaza D5 con el pin que estás usando para el buzzer
buzzer.direction = digitalio.Direction.OUTPUT


def monitor(bpm, angle_xz, angle_yz, mq135):
    if (mq135 == True):
        humo = 'Sin riesgo'
    else:
        humo = 'Riesgo'
    bpm = float(bpm)  # Convierte bpm a un entero
    angle_xz = float(angle_xz)
    angle_yz = float(angle_yz)

    if (bpm < 60 or bpm > 200) or (226 <= angle_xz <= 314) or (mq135 == False):
        lcd.write('Estado: PELIGRO', line=2)
        #BUZZER
        for _ in range(10):
            buzzer.value = True
            time.sleep(0.1)
            buzzer.value = False
            time.sleep(0.1)
        scroll_text(['Estado: PELIGRO', f'BPM: {bpm}', f'Angulo: {angle_xz}', f'Humo: {humo}', 'Estado: PELIGRO'])
        lcd.write('Estado: PELIGRO', line=1)
    elif (60 <= bpm < 100 or 160 < bpm <= 200) or (181 <= angle_xz < 225 or 315 < angle_xz <= 359):
        lcd.write('Estado: ALERTA', line=2)
        #BUZZER
        for _ in range(3):
            buzzer.value = True
            time.sleep(0.2)
            buzzer.value = False
            time.sleep(0.2)
        scroll_text(['Estado: ALERTA', f'BPM: {bpm}', f'Angulo: {angle_xz}', f'Humo: {humo}', 'Estado: ALERTA'])
        lcd.write('Estado: ALERTA', line=1)
    elif (100 <= bpm <= 160) or (0 <= angle_xz <= 180) or (mq135 == True):
        lcd.write('Estado: NORMAL', line=2)
        #BUZZER
        buzzer.value = False  # Apaga el buzzer
        scroll_text(['Estado: NORMAL', f'BPM: {bpm}', f'Angulo: {angle_xz}', f'Humo: {humo}', 'Estado: NORMAL'])
        lcd.write('Estado: NORMAL', line=1)


def scroll_text(text_lines, delay=2):
    # Asegúrate de que text_lines es una lista de cadenas de texto
    if not isinstance(text_lines, list):
        text_lines = [text_lines]

    # Limpia la pantalla antes de empezar
    lcd.clear()

    # Recorre cada línea de texto
    for i in range(len(text_lines)):
        # Si hay una línea anterior, escríbela en la primera línea de la pantalla
        if i > 0:
            lcd.write(text_lines[i - 1], line=1)

        # Escribe la línea actual en la segunda línea de la pantalla
        lcd.write(text_lines[i], line=2)

        # Espera un poco antes de actualizar la pantalla
        time.sleep(delay)

        # Limpia la pantalla antes de escribir las siguientes líneas
        lcd.clear()


contador = 0
while True:
    lcd.write(' Monitor de BEBE', line=1)
    packet = rfm9x.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    packet = rfm9x.receive(timeout=15.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        LED.value = False
        print("Received nothing! Listening again...")
    else:
        # Received a packet!
        LED.value = True
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        #try:
        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))
        # Split the packet_text into its components
        components = packet_text.split(',')
        bpm = components[0].split(':')[1].strip()
        angle_xz = components[1].split(':')[1].strip()
        angle_yz = components[2].split(':')[1].strip()
        # Limpia el display
        lcd.clear()
        # Print the extracted values
        print(f"BPM: {bpm}, Angle XZ: {angle_xz}, Angle YZ: {angle_yz}, Smoke: {mq135.value}")
        #print("\nTemperature: %0.1f C" % bme280.temperature)
        #print("Humidity: %0.1f %%" % bme280.relative_humidity)
        monitor(bpm, angle_xz, angle_yz, mq135.value)
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
        #except Exception as e:
        #print("Ha ocurrido un error: ", e)


