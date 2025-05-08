import RPi.GPIO as GPIO
import time
import subprocess
import threading
from RPLCD import CharLCD
import os
import signal

# LCD config
lcd = CharLCD(
    cols=16, rows=2,
    pin_rs=26,
    pin_e=19,
    pins_data=[13, 6, 5, 11],
    numbering_mode=GPIO.BCM
)

lcd.clear()

# Pines
filas = [16, 20, 21, 12]
columnas = [17, 22, 27, 24]

for fila in filas:
    GPIO.setup(fila, GPIO.OUT)
    GPIO.output(fila, GPIO.HIGH)

for columna in columnas:
    GPIO.setup(columna, GPIO.IN, pull_up_down=GPIO.PUD_UP)

teclado = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Referencias a procesos activos
procesos = {}

# Funciones para ejecutar scripts
def lanzar_script(nombre, ruta):
    proc = subprocess.Popen(['python3', ruta])
    procesos[nombre] = proc
    print(f"{nombre} ejecutándose con PID {proc.pid}")

def detener_todo():
    print("Deteniendo todos los procesos...")

    # Detener scripts lanzados
    for nombre, proc in procesos.items():
        if proc.poll() is None:  # Si aún está corriendo
            print(f"Matando {nombre} (PID {proc.pid})")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    procesos.clear()

    # Cerrar puerto 5000
    try:
        resultado = subprocess.check_output("lsof -ti :5000", shell=True).decode().strip()
        if resultado:
            pids = resultado.split('\n')
            for pid in pids:
                print(f"Matando proceso en puerto 5000 (PID {pid})")
                os.kill(int(pid), signal.SIGTERM)
        else:
            print("Ningún proceso en puerto 5000.")
    except subprocess.CalledProcessError:
        print("No se encontró proceso en puerto 5000.")

def detectar_tecla():
    for i in range(4):
        GPIO.output(filas[i], GPIO.LOW)
        for j in range(4):
            if GPIO.input(columnas[j]) == GPIO.LOW:
                tecla = teclado[i][j]
                lcd.clear()
                lcd.write_string(f"Tecla: {tecla}")
                if tecla == 'A':
                    threading.Thread(target=lanzar_script, args=('script_a', '/var/www/html/rasp/gestos/detect_gesture.py')).start()
                    lcd.clear()
                    lcd.write_string("Abriendo...")
                elif tecla == 'B':
                    threading.Thread(target=lanzar_script, args=('script_b', '/var/www/html/rasp/gestos/collect_gesture.py')).start()
                    lcd.clear()
                    lcd.write_string("Iniciando...")
                elif tecla == 'C':
                    threading.Thread(target=lanzar_script, args=('script_c', '/var/www/html/rasp/gestos/train_model.py')).start()
                    lcd.clear()
                    lcd.write_string("Entrenando...")
                elif tecla == 'D':
                    detener_todo()
                    lcd.clear()
                    lcd.write_string("Cerrando...")
                time.sleep(0.3)
        GPIO.output(filas[i], GPIO.HIGH)
    time.sleep(0.1)

try:
    print("Esperando teclas...")
    while True:
        detectar_tecla()
except KeyboardInterrupt:
    GPIO.cleanup()
    print("GPIO limpio. Programa finalizado.")
