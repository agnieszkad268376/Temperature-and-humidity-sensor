import serial
import time
import re
import PySimpleGUI as sg
from threading import Thread

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

# Layout for the initial window
layout = [[sg.Text("Wybierz swojego kwiatka")],
          [sg.Combo(['Storczyk', 'Monstera', 'Pieniążek', 'Fikus'], default_value='', readonly=True, key='-FLOWER-')],
          [sg.Text("Nazwij swojego kwiatka")],
          [sg.InputText(key='-NAME-')],
          [sg.Button('Submit')]]

# Layout for the homepage window
layout_home = [
    [sg.Column([
        [sg.Button('Chart', size=(10, 1))],
        [sg.Text("Pokaż średnią z:")],
        [sg.Combo(['5 minut', '30 minut', '1 godziny'], default_value='', readonly=True)]
    ]),
    sg.VerticalSeparator(),
    sg.Column([
        [sg.Text("Twój kwiatek czuje się w porządku!")],
        [sg.Text("Temperature"), sg.Text("Wilgotność")]
    ])]
]

# Create both windows with finalize=True
window = sg.Window('Main', layout, finalize=True)
homepage_window = sg.Window('homepage', layout_home, finalize=True)
homepage_window.hide()  # Hide the homepage window initially

# Function to handle sensor data reading
def handle_sensor_data():
    global minute_counter, five_minute_counter, thirty_minute_counter
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

        if humidity is not None:
            mean_humidity.append(humidity)
        if temperature is not None:
            mean_temperature.append(temperature)

        # Odczytanie co minute
        if len(mean_humidity) >= 60 and len(mean_temperature) >= 60:
            #średnia wartość
            avg_humidity = sum(mean_humidity) / len(mean_humidity)
            avg_temperature = sum(mean_temperature) / len(mean_temperature)

            print(f"Average Humidity: {avg_humidity:.2f}%")
            print(f"Average Temperature: {avg_temperature:.2f}C")

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
                    print(f"5-Minute Average Humidity: {avg_five_min_humidity:.2f}%")
                    print(f"5-Minute Average Temperature: {avg_five_min_temperature:.2f}C")

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
                    print(f"30-Minute Average Humidity: {avg_thirty_min_humidity:.2f}%")
                    print(f"30-Minute Average Temperature: {avg_thirty_min_temperature:.2f}C")

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
                    print(f"Hourly Average Humidity: {avg_hour_humidity:.2f}%")
                    print(f"Hourly Average Temperature: {avg_hour_temperature:.2f}C")

                # Dodaj do tablic godzinowych średnich
                hour_mean_humidity.append(avg_hour_humidity)
                hour_mean_temperature.append(avg_hour_temperature)

                # Wyczyść listy dla następnych 60 minut
                thirty_minute_mean_humidity = []
                thirty_minute_mean_temperature = []
                thirty_minute_counter = 0

        time.sleep(1)  # Opóźnienie między kolejnymi odczytami

# Event Loop to process "events" and get the "values" of the inputs
window_active, homepage_active = True, False

# Start the sensor data handling in a separate thread
sensor_thread = Thread(target=handle_sensor_data, daemon=True)
sensor_thread.start()

while True:
    while window_active:
        event, values = window.read(timeout=100)

        if event == sg.WIN_CLOSED:
            window_active = False
            break

        if event == 'Submit':
            flower = values['-FLOWER-']
            name = values['-NAME-']
            if not flower or not name:
                sg.popup('Error', 'All fields must be filled in!')
            else:
                print('Hello', name, '!')
                window.hide()
                homepage_window.un_hide()
                homepage_active = True
                window_active = False
                break

    while homepage_active:
        event, values = homepage_window.read(timeout=100)

        if event == sg.WIN_CLOSED:
            homepage_active = False
            break

    time.sleep(1)  # Opóźnienie między kolejnymi odczytami

ser.close()
window.close()
homepage_window.close()
