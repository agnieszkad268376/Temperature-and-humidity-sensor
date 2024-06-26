import serial
import time
import re
import PySimpleGUI as sg

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

# tablice do przechowywania danych
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

# Obliczanie liczania średnich wartości z ostatnich 5 minut
def five_minute_mean(humidities, temperatures):
    if len(humidities) >= 5 and len(temperatures) >= 5:
        avg_five_min_humidity = sum(humidities) / len(humidities)
        avg_five_min_temperature = sum(temperatures) / len(temperatures)
        return avg_five_min_humidity, avg_five_min_temperature
    return None, None

# Obliczanie liczania średnich wartości z ostatnich 30 minut
def thirty_minute_mean(humidities, temperatures):
    if len(humidities) >= 6 and len(temperatures) >= 6:
        avg_thirty_min_humidity = sum(humidities) / len(humidities)
        avg_thirty_min_temperature = sum(temperatures) / len(temperatures)
        return avg_thirty_min_humidity, avg_thirty_min_temperature
    return None, None

# Obliczanie liczania średnich wartości z ostatnich 60 minut
def hour_mean(humidities, temperatures):
    if len(humidities) >= 2 and len(temperatures) >= 2:
        avg_hour_humidity = sum(humidities) / len(humidities)
        avg_hour_temperature = sum(temperatures) / len(temperatures)
        return avg_hour_humidity, avg_hour_temperature
    return None, None

# Layout for PySimpleGUI
layout = [
    [sg.Text("Current Readings")],
    [sg.Text("Humidity:", size=(20, 1)), sg.Text("", size=(20, 1), key="humidity")],
    [sg.Text("Temperature:", size=(20, 1)), sg.Text("", size=(20, 1), key="temperature")],
    [sg.Text("Average Readings (Last Minute)")],
    [sg.Text("Average Humidity:", size=(20, 1)), sg.Text("", size=(20, 1), key="avg_humidity")],
    [sg.Text("Average Temperature:", size=(20, 1)), sg.Text("", size=(20, 1), key="avg_temperature")],
    [sg.Text("Average Readings (Last 5 Minutes)")],
    [sg.Text("5-Minute Average Humidity:", size=(20, 1)), sg.Text("", size=(20, 1), key="avg_five_min_humidity")],
    [sg.Text("5-Minute Average Temperature:", size=(20, 1)), sg.Text("", size=(20, 1), key="avg_five_min_temperature")],
    [sg.Text("Average Readings (Last 30 Minutes)")],
    [sg.Text("30-Minute Average Humidity:", size=(20, 1)), sg.Text("", size=(20, 1), key="avg_thirty_min_humidity")],
    [sg.Text("30-Minute Average Temperature:", size=(20, 1)), sg.Text("", size=(20, 1), key="avg_thirty_min_temperature")],
    [sg.Text("Average Readings (Last Hour)")],
    [sg.Text("Hourly Average Humidity:", size=(20, 1)), sg.Text("", size=(20, 1), key="avg_hour_humidity")],
    [sg.Text("Hourly Average Temperature:", size=(20, 1)), sg.Text("", size=(20, 1), key="avg_hour_temperature")],
    [sg.Button("Exit")]
]

window = sg.Window("Sensor Data Logger", layout)

minute_counter = 0
five_minute_counter = 0
thirty_minute_counter = 0

try:
    while True:
        event, values = window.read(timeout=1000)  # Read every second
        if event == sg.WIN_CLOSED or event == "Exit":
            break

        # Odczyt danych z czujnika
        sensor_data = read_sensor_data()
        humidity_match = re.search(r'Wilgotnosc \(%\): (\d+\.\d+)', sensor_data)
        temperature_match = re.search(r'Temperatura \(C\): (\d+\.\d+)', sensor_data)

        humidity = float(humidity_match.group(1)) if humidity_match else None
        temperature = float(temperature_match.group(1)) if temperature_match else None
        temperature = temperature - 3 if temperature is not None else None

        # Aktualizacja wyświetlania danych
        window["humidity"].update(f"{humidity:.2f}%" if humidity is not None else "N/A")
        window["temperature"].update(f"{temperature:.2f}C" if temperature is not None else "N/A")

        if humidity is not None:
            mean_humidity.append(humidity)
        if temperature is not None:
            mean_temperature.append(temperature)

        # Odczytanie co minute
        if len(mean_humidity) >= 60 and len(mean_temperature) >= 60:
            # średnia wartość
            avg_humidity = sum(mean_humidity) / len(mean_humidity)
            avg_temperature = sum(mean_temperature) / len(mean_temperature)

            # Aktualizacja wyświetlania średnich wartości
            window["avg_humidity"].update(f"{avg_humidity:.2f}%")
            window["avg_temperature"].update(f"{avg_temperature:.2f}C")

            # wyczyszczenie tablicy
            mean_humidity = []
            mean_temperature = []

            minute_mean_humidity.append(avg_humidity)
            minute_mean_temperature.append(avg_temperature)

            minute_counter += 1
            five_minute_counter += 1
            thirty_minute_counter += 1

            # Obliczanie średnich wartości co 5 minut
            if minute_counter >= 5:
                avg_five_min_humidity, avg_five_min_temperature = five_minute_mean(minute_mean_humidity, minute_mean_temperature)
                if avg_five_min_humidity is not None and avg_five_min_temperature is not None:
                    window["avg_five_min_humidity"].update(f"{avg_five_min_humidity:.2f}%")
                    window["avg_five_min_temperature"].update(f"{avg_five_min_temperature:.2f}C")

                # Dodaj do tablic 5-minutowych średnich
                five_minute_mean_humidity.append(avg_five_min_humidity)
                five_minute_mean_temperature.append(avg_five_min_temperature)

                # Wyczyść listy dla następnych 5 minut
                minute_mean_humidity = []
                minute_mean_temperature = []
                minute_counter = 0

            # Obliczanie średnich wartości co 30 minut
            if five_minute_counter >= 6:
                avg_thirty_min_humidity, avg_thirty_min_temperature = thirty_minute_mean(five_minute_mean_humidity, five_minute_mean_temperature)
                if avg_thirty_min_humidity is not None and avg_thirty_min_temperature is not None:
                    window["avg_thirty_min_humidity"].update(f"{avg_thirty_min_humidity:.2f}%")
                    window["avg_thirty_min_temperature"].update(f"{avg_thirty_min_temperature:.2f}C")

                # Dodaj do tablic 30-minutowych średnich
                thirty_minute_mean_humidity.append(avg_thirty_min_humidity)
                thirty_minute_mean_temperature.append(avg_thirty_min_temperature)

                # Wyczyść listy dla następnych 30 minut
                five_minute_mean_humidity = []
                five_minute_mean_temperature = []
                five_minute_counter = 0

            # Obliczanie średnich wartości co godzinę
            if thirty_minute_counter >= 2:
                avg_hour_humidity, avg_hour_temperature = hour_mean(thirty_minute_mean_humidity, thirty_minute_mean_temperature)
                if avg_hour_humidity is not None and avg_hour_temperature is not None:
                    window["avg_hour_humidity"].update(f"{avg_hour_humidity:.2f}%")
                    window["avg_hour_temperature"].update(f"{avg_hour_temperature:.2f}C")

                # Dodaj do tablic godzinowych średnich
                hour_mean_humidity.append(avg_hour_humidity)
                hour_mean_temperature.append(avg_hour_temperature)

                # Wyczyść listy dla następnych 60 minut
                thirty_minute_mean_humidity = []
                thirty_minute_mean_temperature = []
                thirty_minute_counter = 0

except KeyboardInterrupt:
    print("Program terminated by user")
    ser.close()
    window.close()
