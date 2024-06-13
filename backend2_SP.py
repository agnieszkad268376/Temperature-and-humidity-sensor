import serial
import time
import re
from threading import Thread
from queue import Queue

# Ustawienia portu szeregowego
ser = serial.Serial('COM5', 9600, timeout=1)  # Zmień 'COM5' na odpowiedni port
time.sleep(2)  # Czekaj na nawiązanie połączenia

# Function to read sensor data
def read_sensor_data():
    global ser
    ser.write(b'read\n')
    sensor_data = ser.readline().decode().strip()
    return sensor_data

# Queues for sharing data between threads
data_queue = Queue()

# Data processing function
def process_sensor_data():
    mean_humidity = []
    mean_temperature = []
    minute_mean_humidity = []
    minute_mean_temperature = []
    five_minute_mean_humidity = []
    five_minute_mean_temperature = []
    thirty_minute_mean_humidity = []
    thirty_minute_mean_temperature = []
    hour_mean_humidity = []
    hour_mean_temperature = []

    minute_counter = 0
    five_minute_counter = 0
    thirty_minute_counter = 0

    while True:
        sensor_data = read_sensor_data()
        humidity_match = re.search(r'Wilgotnosc \(%\): (\d+\.\d+)', sensor_data)
        temperature_match = re.search(r'Temperatura \(C\): (\d+\.\d+)', sensor_data)

        humidity = float(humidity_match.group(1)) if humidity_match else None
        temperature = float(temperature_match.group(1)) if temperature_match else None
        temperature = temperature - 2 if temperature is not None else None

        if humidity is not None and temperature is not None:
            mean_humidity.append(humidity)
            mean_temperature.append(temperature)

        if len(mean_humidity) >= 60 and len(mean_temperature) >= 60:
            avg_humidity = sum(mean_humidity) / len(mean_humidity)
            avg_temperature = sum(mean_temperature) / len(mean_temperature)

            mean_humidity = []
            mean_temperature = []

            minute_mean_humidity.append(avg_humidity)
            minute_mean_temperature.append(avg_temperature)

            minute_counter += 1
            five_minute_counter += 1
            thirty_minute_counter += 1

            if minute_counter >= 5:
                avg_five_min_humidity, avg_five_min_temperature = five_minute_mean(minute_mean_humidity, minute_mean_temperature)
                if avg_five_min_humidity is not None and avg_five_min_temperature is not None:
                    five_minute_mean_humidity.append(avg_five_min_humidity)
                    five_minute_mean_temperature.append(avg_five_min_temperature)

                minute_mean_humidity = []
                minute_mean_temperature = []
                minute_counter = 0

            if five_minute_counter >= 6:
                avg_thirty_min_humidity, avg_thirty_min_temperature = thirty_minute_mean(five_minute_mean_humidity, five_minute_mean_temperature)
                if avg_thirty_min_humidity is not None and avg_thirty_min_temperature is not None:
                    thirty_minute_mean_humidity.append(avg_thirty_min_humidity)
                    thirty_minute_mean_temperature.append(avg_thirty_min_temperature)

                five_minute_mean_humidity = []
                five_minute_mean_temperature = []
                five_minute_counter = 0

            if thirty_minute_counter >= 2:
                avg_hour_humidity, avg_hour_temperature = hour_mean(thirty_minute_mean_humidity, thirty_minute_mean_temperature)
                if avg_hour_humidity is not None and avg_hour_temperature is not None:
                    hour_mean_humidity.append(avg_hour_humidity)
                    hour_mean_temperature.append(avg_hour_temperature)

                thirty_minute_mean_humidity = []
                thirty_minute_mean_temperature = []
                thirty_minute_counter = 0

        data_queue.put((temperature, humidity, avg_five_min_temperature, avg_five_min_humidity, avg_thirty_min_temperature, avg_thirty_min_humidity, avg_hour_temperature, avg_hour_humidity))
        time.sleep(1)

# Helper functions for calculating means
def five_minute_mean(humidities, temperatures):
    if len(humidities) >= 5 and len(temperatures) >= 5:
        avg_five_min_humidity = sum(humidities) / len(humidities)
        avg_five_min_temperature = sum(temperatures) / len(temperatures)
        return avg_five_min_humidity, avg_five_min_temperature
    return None, None

def thirty_minute_mean(humidities, temperatures):
    if len(humidities) >= 6 and len(temperatures) >= 6:
        avg_thirty_min_humidity = sum(humidities) / len(humidities)
        avg_thirty_min_temperature = sum(temperatures) / len(temperatures)
        return avg_thirty_min_humidity, avg_thirty_min_temperature
    return None, None

def hour_mean(humidities, temperatures):
    if len(humidities) >= 2 and len(temperatures) >= 2:
        avg_hour_humidity = sum(humidities) / len(humidities)
        avg_hour_temperature = sum(temperatures) / len(temperatures)
        return avg_hour_humidity, avg_hour_temperature
    return None, None

# Start the data processing thread
sensor_thread = Thread(target=process_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()
