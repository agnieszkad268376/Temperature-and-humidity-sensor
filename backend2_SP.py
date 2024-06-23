import csv
import datetime
import os
import serial
import time
import re
import PySimpleGUI as sg
from collections import deque
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# Serial port settings
ser = serial.Serial('COM8', 9600, timeout=1)  # Change 'COM8' to your appropriate port
time.sleep(2)  # Wait for the connection to establish

# Function to read data from the sensor
def read_sensor_data():
    global ser
    sensor_data = ser.readline().decode().strip()
    return sensor_data

# Function to calculate mean values from data over a specified number of minutes
def calculate_mean(data, minutes):
    if len(data) < minutes * 10:
        return "N/A"
    return f"{statistics.mean(list(data)[-minutes * 60:]):.2f}"

# Function to determine flower status based on average humidity and temperature
def determine_flower_status(avg_humidity, avg_temperature, flower):
    ranges = {
        "Storczyk": {"humidity": (50, 70), "temperature": (18, 22)},
        "Monstera": {"humidity": (60, 80), "temperature": (20, 25)},
        "Pieniążek": {"humidity": (40, 60), "temperature": (15, 20)},
        "Fikus": {"humidity": (50, 80), "temperature": (20, 24)},
    }

    if flower in ranges:
        humidity_range = ranges[flower]["humidity"]
        temperature_range = ranges[flower]["temperature"]

        # Check humidity and temperature separately
        is_humidity_ok = humidity_range[0] < avg_humidity < humidity_range[1]
        is_temperature_ok = temperature_range[0] < avg_temperature < temperature_range[1]

        # Determine if humidity is too high or too low
        if avg_humidity > humidity_range[1]:
            humidity_status = "zbyt wysoka wilgotność"
        elif avg_humidity < humidity_range[0]:
            humidity_status = "zbyt niska wilgotność"
        else:
            humidity_status = "odpowiednia wilgotność"

        # Determine if temperature is too high or too low
        if avg_temperature > temperature_range[1]:
            temperature_status = "zbyt wysoka temperatura"
        elif avg_temperature < temperature_range[0]:
            temperature_status = "zbyt niska temperatura"
        else:
            temperature_status = "odpowiednia temperatura"

        # Construct the status message based on both humidity and temperature conditions
        if is_humidity_ok and is_temperature_ok:
            return f"Twój {flower} czuje się dobrze - {humidity_status} i {temperature_status}."
        elif is_humidity_ok and not is_temperature_ok:
            return f"Twój {flower} ma odpowiednią wilgotność, ale {temperature_status}."
        elif not is_humidity_ok and is_temperature_ok:
            return f"Twój {flower} ma odpowiednią temperaturę, ale {humidity_status}."
        else:
            return f"Twój {flower} ma nieodpowiednie warunki - {humidity_status} i {temperature_status}."

    return "Mam dziwne dane, sprawdź czy Twój kwiatek żyje"


def save_data(temperature, humidity, avg_five_min_temperature, avg_five_min_humidity,
              avg_thirty_min_temperature, avg_thirty_min_humidity,
              avg_hour_temperature, avg_hour_humidity, filename='sensor_data.txt'):
    # Check if the file exists
    file_exists = os.path.isfile(filename)

    # Open the file in append mode
    with open(filename, mode='a', encoding='utf-8') as file:
        # Get the current date and time
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Write the timestamp and sensor data
        if humidity is not None and temperature is not None:
            file.write(f'Date and Time: {current_time}\n')
            file.write(f'Temperature: {temperature:.2f} Celsius\n')
            file.write(f'Humidity: {humidity:.2f}%\n')

            # Write averages with proper handling for "N/A"
            file.write('Average 5 min temp: ' +
                       (f'{float(avg_five_min_temperature):.2f}' if avg_five_min_temperature != "N/A" else 'N/A') + '\n')
            file.write('Average 5 min humidity: ' +
                       (f'{float(avg_five_min_humidity):.2f}' if avg_five_min_humidity != "N/A" else 'N/A') + '\n')
            file.write('Average 30 min temp: ' +
                       (f'{float(avg_thirty_min_temperature):.2f}' if avg_thirty_min_temperature != "N/A" else 'N/A') + '\n')
            file.write('Average 30 min humidity: ' +
                       (f'{float(avg_thirty_min_humidity):.2f}' if avg_thirty_min_humidity != "N/A" else 'N/A') + '\n')
            file.write('Average 60 min temp: ' +
                       (f'{float(avg_hour_temperature):.2f}' if avg_hour_temperature != "N/A" else 'N/A') + '\n')
            file.write('Average 60 min humidity: ' +
                       (f'{float(avg_hour_humidity):.2f}' if avg_hour_humidity != "N/A" else 'N/A') + '\n')
            file.write('\n')  # Blank line to separate entries


# PySimpleGUI layouts
layout_main = [
    [sg.Text("Wybierz swojego kwiatka")],
    [sg.Combo(['Storczyk', 'Monstera', 'Pieniążek', 'Fikus'], default_value='', readonly=True, key='-FLOWER-')],
    [sg.Text("Nazwij swojego kwiatka")],
    [sg.InputText(key='-NAME-')],
    [sg.Button('Submit')]
]

layout_sensor = [
    [sg.Text("Current Readings")],
    [sg.Text("Temperature:"), sg.Text("", key="temperature")],
    [sg.Text("Humidity:"), sg.Text("", key="humidity")],
    [sg.Text("5-Minute Average:"), sg.Text("", key="avg_five_min_temperature"), sg.Text("", key="avg_five_min_humidity")],
    [sg.Text("30-Minute Average:"), sg.Text("", key="avg_thirty_min_temperature"), sg.Text("", key="avg_thirty_min_humidity")],
    [sg.Text("60-Minute Average:"), sg.Text("", key="avg_hour_temperature"), sg.Text("", key="avg_hour_humidity")],
    [sg.Text("Status: "), sg.Text("Trwa pomiar", key='-STATUS-')],
    [sg.Button('Chart'), sg.Button("Save"), sg.Button("Exit")]
]

layout_chart = [
    [sg.Text("Temperature Chart")],
    [sg.Canvas(key='-CANVAS_TEMP-', size=(400, 200))],
    [sg.Text("Humidity Chart")],
    [sg.Canvas(key='-CANVAS_HUMIDITY-', size=(400, 200))],
    [sg.Button('Back')]
]

# Creating windows
window_main = sg.Window("Main", layout_main)
window_sensor = sg.Window("Sensor Data Logger", layout_sensor, finalize=True)
window_chart = sg.Window("Chart", layout_chart, finalize=True, element_justification='center')
window_sensor.hide()
window_chart.hide()

# Data queues for storing humidity and temperature data
humidity_data = deque(maxlen=3600)  # Store up to 1 hour of data (3600 seconds)
temperature_data = deque(maxlen=3600)

# Matplotlib setup for charts
fig_temp, ax_temp = plt.subplots(figsize=(4, 2))  # Smaller figure size
fig_humid, ax_humid = plt.subplots(figsize=(4, 2))  # Smaller figure size

canvas_temp = FigureCanvasTkAgg(fig_temp, master=window_chart['-CANVAS_TEMP-'].TKCanvas)
canvas_temp.get_tk_widget().pack()
canvas_temp.draw()

canvas_humid = FigureCanvasTkAgg(fig_humid, master=window_chart['-CANVAS_HUMIDITY-'].TKCanvas)
canvas_humid.get_tk_widget().pack()
canvas_humid.draw()

def update_chart(i):
    global ax_temp, ax_humid, canvas_temp, canvas_humid, humidity_data, temperature_data

    ax_temp.clear()
    ax_humid.clear()
    ax_temp.set_xlabel('Time (seconds)')
    ax_temp.set_ylabel('Temperature (C)')
    ax_humid.set_xlabel('Time (seconds)')
    ax_humid.set_ylabel('Humidity (%)')

    if len(temperature_data) > 50:
        temp_range = range(len(temperature_data))[-50:]
        temp_data = list(temperature_data)[-50:]
    else:
        temp_range = range(len(temperature_data))
        temp_data = list(temperature_data)

    if len(humidity_data) > 50:
        humid_range = range(len(humidity_data))[-50:]
        humid_data = list(humidity_data)[-50:]
    else:
        humid_range = range(len(humidity_data))
        humid_data = list(humidity_data)

    ax_temp.plot(temp_range, temp_data, label='Temperature (C)')
    ax_humid.plot(humid_range, humid_data, label='Humidity (%)')

    ax_temp.legend(loc='upper left')
    ax_humid.legend(loc='upper left')
    ax_temp.grid()
    ax_humid.grid()

    canvas_temp.draw()
    canvas_humid.draw()

try:
    while True:
        # Read sensor data
        sensor_data = read_sensor_data()
        humidity_match = re.search(r'Wilgotnosc \(%\): (\d+\.\d+)', sensor_data)
        temperature_match = re.search(r'Temperatura \(C\): (\d+\.\d+)', sensor_data)

        humidity = float(humidity_match.group(1)) if humidity_match else None
        temperature = float(temperature_match.group(1)) if temperature_match else None
        temperature = temperature - 3 if temperature is not None else None

        # Calculate and update average values
        avg_five_min_humidity = calculate_mean(humidity_data, 5)
        avg_five_min_temperature = calculate_mean(temperature_data, 5)
        avg_thirty_min_humidity = calculate_mean(humidity_data, 30)
        avg_thirty_min_temperature = calculate_mean(temperature_data, 30)
        avg_hour_humidity = calculate_mean(humidity_data, 60)
        avg_hour_temperature = calculate_mean(temperature_data, 60)

        print(humidity)
        print(temperature)
        event_main, values_main = window_main.read(timeout=100)
        if event_main == sg.WIN_CLOSED:
            break
        if event_main == 'Submit':
            flower = values_main['-FLOWER-']
            name = values_main['-NAME-']
            if not flower or not name:
                sg.popup('Error', 'All fields must be filled in!')
            else:
                print('Hello', name, '!')
                window_main.hide()
                window_sensor.un_hide()

        event_sensor, values_sensor = window_sensor.read(timeout=1000)
        if event_sensor == sg.WIN_CLOSED or event_sensor == "Exit":
            break
        if event_sensor == 'Chart':
            window_sensor.hide()
            window_chart.un_hide()
            ani = FuncAnimation(fig_temp, update_chart, interval=1000)  # Update chart every second
            ani = FuncAnimation(fig_humid, update_chart, interval=1000)  # Update chart every second
        if event_sensor == 'Save':
            if temperature is not None and humidity is not None:
                save_data(temperature, humidity, avg_five_min_temperature, avg_five_min_humidity,
                          avg_thirty_min_temperature, avg_thirty_min_humidity,
                          avg_hour_temperature, avg_hour_humidity)
                sg.popup('Data Saved', 'Sensor data has been saved successfully in C:\PYTHON\programy z pythona\semestr6 directory.')
            else:
                sg.popup('Error', 'No data to save.')
        event_chart, values_chart = window_chart.read(timeout=1000)
        if event_chart == sg.WIN_CLOSED or event_chart == "Back":
            window_chart.hide()
            window_sensor.un_hide()

        # Update GUI with current sensor readings
        window_sensor["humidity"].update(f"{humidity:.2f}%" if humidity is not None else "N/A")
        window_sensor["temperature"].update(f"{temperature:.2f}C" if temperature is not None else "N/A")

        # Append data to queues if available
        if humidity is not None:
            humidity_data.append(humidity)
        if temperature is not None:
            temperature_data.append(temperature)

        window_sensor["avg_five_min_humidity"].update(avg_five_min_humidity)
        window_sensor["avg_five_min_temperature"].update(f"{avg_five_min_temperature}")
        window_sensor["avg_thirty_min_humidity"].update(avg_thirty_min_humidity)
        window_sensor["avg_thirty_min_temperature"].update(f"{avg_thirty_min_temperature}")
        window_sensor["avg_hour_humidity"].update(avg_hour_humidity)
        window_sensor["avg_hour_temperature"].update(f"{avg_hour_temperature}")

        # Determine flower status and update status text
        if avg_five_min_humidity != "N/A" and avg_five_min_temperature != "N/A":
            status = determine_flower_status(float(avg_five_min_humidity), float(avg_five_min_temperature), flower)
            window_sensor["-STATUS-"].update(status)

except KeyboardInterrupt:
    print("Program terminated by user")
    ser.close()

finally:
    ser.close()
    window_sensor.close()
    window_main.close()
