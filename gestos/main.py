from RPLCD.gpio import CharLCD
from RPi import GPIO
from time import sleep

# Configuración del LCD en modo 4 bits
lcd = CharLCD(
    cols=16, rows=2,                 # LCD 16x2
    pin_rs=26,                       # RS
    pin_e=19,                        # Enable
    pins_data=[13, 6, 5, 11],        # D4, D5, D6, D7
    numbering_mode=GPIO.BCM          # Usamos numeración BCM
)

# Limpiamos la pantalla por si acaso
lcd.clear()

# Mostrar "Hola mundo"
lcd.write_string("EMERSON")

# Espera para que puedas verlo
sleep(5)

# Limpiar y finalizar
lcd.clear()
lcd.write_string("HOLA MUNDO :)")
sleep(2)
lcd.clear()
