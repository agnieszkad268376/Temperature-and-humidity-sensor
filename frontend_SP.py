import PySimpleGUI as sg
import threading  # Import threading for running the backend in a separate thread
import backend2_SP  # Import your backend script

# Define flower preferences
flower_preferences = {
    'Storczyk': {'temp': 20, 'humidity': 60},
    'Monstera': {'temp': 22, 'humidity': 50},
    'Pieniążek': {'temp': 24, 'humidity': 70},
    'Fikus': {'temp': 21, 'humidity': 65}
}

# Layout for the initial window
layout = [
    [sg.Text("Wybierz swojego kwiatka")],
    [sg.Combo(['Storczyk', 'Monstera', 'Pieniążek', 'Fikus'], default_value='', readonly=True, key='-FLOWER-')],
    [sg.Text("Nazwij swojego kwiatka")],
    [sg.InputText(key='-NAME-')],
    [sg.Button('Submit')]
]

# Layout for the homepage window
layout_home = [
    [sg.Column([
        [sg.Button('Chart', size=(10, 1))],
        [sg.Text("Pokaż średnią z:")],
        [sg.Combo(['5 minut', '30 minut', '1 godziny'], default_value='5 minut', readonly=True, key='-MEAN-')]
    ]),
        sg.VerticalSeparator(),
        sg.Column([
            [sg.Text("Twój kwiatek czuje się w porządku!", key='-STATUS-')],
            [sg.Text("Temperature: "), sg.Text("", key='-TEMP-')],
            [sg.Text("Wilgotność: "), sg.Text("", key='-HUM-')],
            [sg.Text("Średnia temperatura: "), sg.Text("N/A", key='-MEAN-TEMP-')],
            [sg.Text("Średnia wilgotność: "), sg.Text("N/A", key='-MEAN-HUM-')]
        ])]
]

# Create both windows with finalize=True
window = sg.Window('Main', layout, finalize=True)
homepage_window = sg.Window('homepage', layout_home, finalize=True)
homepage_window.hide()  # Hide the homepage window initially

# Function to start backend processing in a separate thread
def start_backend():
    backend2_SP.process_sensor_data()

# Start the backend processing in a separate thread
backend_thread = threading.Thread(target=start_backend)
backend_thread.daemon = True  # Daemonize the thread so it exits when the main program exits
backend_thread.start()

# Event Loop to process "events" and get the "values" of the inputs
window_active, homepage_active = True, False

while True:
    while window_active:
        event, values = window.read()

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
        event, values = homepage_window.read(timeout=2000)

        if event == sg.WIN_CLOSED:
            homepage_active = False
            break

        # Update GUI elements with sensor data
        temperature_store = backend2_SP.temperature_store
        humidity_store = backend2_SP.humidity_store

        if temperature_store:
            temperature = temperature_store[-1]
            homepage_window['-TEMP-'].update(f"{temperature:.2f} C")

        if humidity_store:
            humidity = humidity_store[-1]
            homepage_window['-HUM-'].update(f"{humidity:.2f} %")

        # Update mean values based on selected period
        mean_period = values['-MEAN-']
        if mean_period == '5 minut':
            mean_temp = sum(temperature_store[-5:]) / len(temperature_store[-5:]) if temperature_store else None
            mean_hum = sum(humidity_store[-5:]) / len(humidity_store[-5:]) if humidity_store else None
        elif mean_period == '30 minut':
            mean_temp = sum(temperature_store[-30:]) / len(temperature_store[-30:]) if temperature_store else None
            mean_hum = sum(humidity_store[-30:]) / len(humidity_store[-30:]) if humidity_store else None
        elif mean_period == '1 godziny':
            mean_temp = sum(temperature_store[-60:]) / len(temperature_store[-60:]) if temperature_store else None
            mean_hum = sum(humidity_store[-60:]) / len(humidity_store[-60:]) if humidity_store else None
        else:
            mean_temp = mean_hum = None

        homepage_window['-MEAN-TEMP-'].update(f"{mean_temp:.2f} C" if mean_temp is not None else "N/A")
        homepage_window['-MEAN-HUM-'].update(f"{mean_hum:.2f} %" if mean_hum is not None else "N/A")

        # Update status based on current flower selection
        current_flower = values['-FLOWER-']
        if current_flower in flower_preferences:
            pref_temp = flower_preferences[current_flower]['temp']
            pref_hum = flower_preferences[current_flower]['humidity']

            if temperature is not None and humidity is not None:
                if pref_temp <= temperature <= pref_hum:
                    homepage_window['-STATUS-'].update(f"Twój kwiatek czuje się w porządku!")
                else:
                    homepage_window['-STATUS-'].update(f"Twój kwiatek nie czuje się dobrze!")

window.close()
homepage_window.close()