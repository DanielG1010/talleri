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

contador = 0
while True:
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
        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))
        # Split the packet_text into its components
        components = packet_text.split(',')
        bpm = int(components[0].split(':')[1].strip())
        angle_xz = int(components[1].split(':')[1].strip())
        angle_yz = int(components[2].split(':')[1].strip())

        # Print the extracted values
        print(f"BPM: {bpm}, Angle XZ: {angle_xz}, Angle YZ: {angle_yz}")
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))