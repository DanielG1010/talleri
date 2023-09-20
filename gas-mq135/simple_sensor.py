import time
import board
import digitalio
import analogio

buzzerPin = digitalio.DigitalInOut(board.D10)
buzzerPin.direction = digitalio.Direction.OUTPUT

greenLED = digitalio.DigitalInOut(board.D11)
greenLED.direction = digitalio.Direction.OUTPUT

redLED = digitalio.DigitalInOut(board.D12)
redLED.direction = digitalio.Direction.OUTPUT

sensorPin = analogio.AnalogIn(board.A5)

while True:
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

    time.sleep(0.1)

