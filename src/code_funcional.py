import time
import board
import busio
import digitalio
import adafruit_rfm9x
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_bh1750
from analogio import AnalogIn
from digitalio import DigitalInOut


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
    rfm9x.send(bytes(data, "UTF-8"))
    ack = rec_ack()
    while not ack:
        print("Acknowledge {}".format(ack))
        rfm9x.send(bytes(data, "UTF-8"))
        ack = rec_ack()
