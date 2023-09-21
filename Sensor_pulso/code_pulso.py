import machine
import time

# Configura el módulo ADC para la lectura analógica en el pin 32 (ajusta el pin según corresponda)
adc = machine.ADC(machine.Pin(32))

# Establece el umbral (threshold) para la lectura analógica
umbral = 1500  # Depende de la señal del sensor

# Inicializa los contadores
contador_10s = 0

# Tiempo en segundos para la duración del conteo y la lectura del sensor (10 segundos en este caso)
duracion_conteo = 10
over = 0
over_ant = over
tiempo_inicial_min = time.time()
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
        #Se retorna la bandera de over(threshold) a 0         
        else:
            over = 0
               
        if over != over_ant:       #Se muestra cuando la señal de over(threshold) cambia, para comprobación
            mensaje = "El estado anterior de over era " + str(over_ant) + " y ahora es " + str(over)
            print(mensaje)

        over_ant = over

    # Calcula el conteo aproximado en 1 minuto
    pulso_por_min = contador_10s*6
    print("Se superó el umbral", contador_10s, "veces en los últimos 10 segundos.")
    print("La cantidad es aprox", pulso_por_min, "pulsos por minuto")
    
    
    contador_10s = 0  # Reinicia el contador de 10 segundos

