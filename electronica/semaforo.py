import serial
import time


PORT = "/dev/ttyACM0"
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

print("=== CONTROL DE SEMAFORO DESDE PYTHON ===")
print("Escribe 'salir' en cualquier momento para terminar.\n")

while True:
    try:
        
        tVerde = input("Tiempo VERDE (seg): ")
        if tVerde.lower() == "salir":
            break

        tAmarillo = input("Tiempo AMARILLO (seg): ")
        if tAmarillo.lower() == "salir":
            break

        tRojo = input("Tiempo ROJO (seg): ")
        if tRojo.lower() == "salir":
            break

        
        mensaje = f"{tVerde},{tAmarillo},{tRojo}\n"
        ser.write(mensaje.encode())
        print(">>> Valores enviados al Arduino.\n")

    except KeyboardInterrupt:
        break


print("Apagando LEDs y cerrando conexión...")
ser.write(b"STOP\n")
time.sleep(1)
ser.close()
print("Listo.")
