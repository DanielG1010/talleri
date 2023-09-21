import time
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import adafruit_character_lcd.character_lcd_i2c as character_lcd

# Modifica esto si tienes un LCD de caracteres de diferente tamaño
lcd_columns = 16
lcd_rows = 2

# Inicializa el bus I2C.
i2c = board.I2C()  # usa board.SCL y board.SDA

# Inicializa la clase lcd
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows)

# Dirección I2C del Feather
feather_address = 0x00  # Reemplaza esto con la dirección I2C de tu Feather

# Crea una instancia del dispositivo I2C para el Feather
feather_device = I2CDevice(i2c, feather_address)

# Enciende la luz de fondo
lcd.backlight = True

while True:
    with feather_device:
        # Lee los datos enviados por el Feather (modifica el número de bytes según sea necesario)
        data = bytearray(32)
        feather_device.readinto(data)
        # Convierte los datos a string
        message = data.decode('utf-8').strip('\x00')
        # Imprime el mensaje en el LCD
        lcd.message = message
    # Espera un poco antes de leer el siguiente mensaje
    time.sleep(0.1)



