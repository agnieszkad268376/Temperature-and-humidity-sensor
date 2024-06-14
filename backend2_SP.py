import serial
import time
import re

ser = serial.Serial('COM5', 9600, timeout=1)  # Replace 'COM5' with your actual serial port
time.sleep(2)  # Wait for the serial connection to establish

temperature_store = []
humidity_store = []

def read_sensor_data():
    global ser
    ser.write(b'read\n')
    sensor_data = ser.readline().decode().strip()
    return sensor_data


def process_sensor_data():
    global temperature_store, humidity_store
    while True:
        sensor_data = read_sensor_data()
        humidity_match = re.search(r'Wilgotnosc \(%\): (\d+\.\d+)', sensor_data)
        temperature_match = re.search(r'Temperatura \(C\): (\d+\.\d+)', sensor_data)

        humidity = float(humidity_match.group(1)) if humidity_match else None
        temperature = float(temperature_match.group(1)) if temperature_match else None
        temperature = temperature - 2 if temperature is not None else None

        temperature_store.append(temperature)
        humidity_store.append(humidity)

        time.sleep(1)