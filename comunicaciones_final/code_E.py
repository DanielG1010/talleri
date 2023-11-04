import board
import busio
import digitalio
import analogio
import time
from math import atan2, degrees
import adafruit_mpu6050
import adafruit_rfm9x

RADIO_FREQ_MHZ = 915.0
TIEMPO_ENVIO = 5
CS = digitalio.DigitalInOut(board.RFM9X_CS)
RESET = digitalio.DigitalInOut(board.RFM9X_RST)
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23
i2c = board.I2C()
sensor = adafruit_mpu6050.MPU6050(i2c)
contador = 0
light = analogio.AnalogIn(board.A0)

def vector_2_degrees(x, y):
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle

# Given an accelerometer sensor object, return the inclination angles of X/Z and Y/Z
def get_inclination(_sensor):
    x, y, z = _sensor.acceleration
    return vector_2_degrees(x, z), vector_2_degrees(y, z)

# Heart rate sensor init
def get_bpm_and_angles(sensor):
    umbral = 450
    contador_picos = 0
    duracion_conteo = 15
    tiempo_inicial = time.monotonic()
    estado_umbral = False


    NUM_OVERSAMPLE = 10
    NUM_SAMPLES = 20
    samples = [0] * NUM_SAMPLES
    while (time.monotonic() - tiempo_inicial <= duracion_conteo):
        for i in range(NUM_SAMPLES):
            oversample = 0
            for s in range(NUM_OVERSAMPLE):
                oversample += float(light.value)
            samples[i] = oversample / NUM_OVERSAMPLE

            mean = sum(samples) / float(len(samples))
            center = samples[i] - mean

            if center > umbral:
                if not estado_umbral:
                    contador_picos += 1
                    estado_umbral = True
            else:
                estado_umbral = False
        if time.monotonic() - tiempo_inicial >= duracion_conteo:
            bpm = contador_picos * (60 / duracion_conteo)
            angle_xz, angle_yz = get_inclination(sensor)
            return str(bpm), str(angle_xz), str(angle_yz)

    # Return default values if the condition is not met
    return "N/A", "N/A", "N/A"


while True:
    if contador == TIEMPO_ENVIO:
        contador = 0
        # Get BPM and angles
        bpm, angle_xz, angle_yz = get_bpm_and_angles(sensor)  # Make sure to implement this function
        data_to_send = f"BPM: {bpm}, Angle XZ: {angle_xz}, Angle YZ: {angle_yz}"

        rfm9x.send(data_to_send)
        print(f"Sent data: {data_to_send}")
        print("Waiting for packets...")
    else:
        contador += 1
    time.sleep(1)
