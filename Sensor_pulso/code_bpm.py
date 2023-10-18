# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time

import analogio
import board

# import neopixel
# Establece el umbral para la detección de picos
umbral = 225

# Inicializa el contador de picos
contador_picos = 0

# Tiempo en segundos para la duración del conteo (15 segundos en este caso)
duracion_conteo = 15

# Tiempo inicial para el conteo actual
tiempo_inicial = time.monotonic()

# Estado del umbral (True si la señal está por encima del umbral, False si está por debajo)
estado_umbral = False
# pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=1.0)
# light = analogio.AnalogIn(board.LIGHT)
light = analogio.AnalogIn(board.A0)

# Turn only pixel #1 green
# pixels[1] = (0, 255, 0)

# How many light readings per sample
NUM_OVERSAMPLE = 10
# How many samples we take to calculate 'average'
NUM_SAMPLES = 20
samples = [0] * NUM_SAMPLES

while True:
    for i in range(NUM_SAMPLES):
        # Take NUM_OVERSAMPLE number of readings really fast
        oversample = 0
        for s in range(NUM_OVERSAMPLE):
            oversample += float(light.value)
        # and save the average from the oversamples
        samples[i] = oversample / NUM_OVERSAMPLE  # Find the average

        mean = sum(samples) / float(len(samples))  # take the average
        #print((samples[i] - mean,))  # 'center' the reading
        time.sleep(0.025)  # change to go faster/slower
        # Compara la lectura con el umbral
        center = samples[i] - mean
        
        if center > umbral:
            # Si la señal acaba de pasar por encima del umbral...
            if not estado_umbral:
                contador_picos += 1  # Aumenta el contador de picos
                estado_umbral = True
        else:
            # Si la señal está por debajo del umbral...
            estado_umbral = False

        # Si han pasado 15 segundos...
        if time.monotonic() - tiempo_inicial >= duracion_conteo:
            # Calcula los BPM
            bpm = contador_picos * (60 / duracion_conteo)
            print("BPM:", bpm)

            # Reinicia el contador y el tiempo inicial
            contador_picos = 0
            tiempo_inicial = time.monotonic()


        # time.sleep(0.01)  # Pequeña pausa para evitar la sobrecarga de la CPU

