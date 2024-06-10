import serial
import time
import re

# Ustawienia portu szeregowego
ser = serial.Serial('COM5', 9600, timeout=1)  # Zmień 'COM5' na odpowiedni port
time.sleep(2)  # Czekaj na nawiązanie połączenia

# Funkcja do odczytu danych z czujnika
def read_sensor_data():
    global ser
    # Wysłanie komendy do Arduino, aby rozpoczął odczyt danych
    ser.write(b'read\n')
    # Odczyt danych z portu szeregowego
    sensor_data = ser.readline().decode().strip()
    return sensor_data

try:
    while True:
        # Odczyt danych z czujnika
        sensor_data = read_sensor_data()
        humidity_match = re.search(r'Wilgotnosc \(%\): (\d+\.\d+)', sensor_data)
        temperature_match = re.search(r'Temperatura \(C\): (\d+\.\d+)', sensor_data)

        humidity = float(humidity_match.group(1)) if humidity_match else None
        temperature = float(temperature_match.group(1)) if temperature_match else None
        temperature = temperature - 3 if temperature is not None else None

        # Wyświetlenie danych w terminalu
        print("Humidity:", humidity, "Temperature:", temperature)
        #print("Sensor data:", sensor_data)
        time.sleep(1)  # Opóźnienie między kolejnymi odczytami
except KeyboardInterrupt:
    print("Program terminated by user")
    ser.close()
