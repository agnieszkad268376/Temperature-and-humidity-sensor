import PySimpleGUI as sg
from queue import Queue
from threading import Thread

# Shared queue to get data from the backend
data_queue = Queue()
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


# Function to update GUI elements based on data_queue
def update_gui():
    while True:
        event, values = homepage_window.read(timeout=1000)

        if event == sg.WIN_CLOSED:
            break

        # Read sensor data from the queue
        if not data_queue.empty():
            temperature, humidity, alert, avg_five_min_temperature, avg_five_min_humidity, avg_thirty_min_temperature, avg_thirty_min_humidity, avg_hour_temperature, avg_hour_humidity = data_queue.get()

            homepage_window['-TEMP-'].update(f"{temperature:.2f} C")
            homepage_window['-HUM-'].update(f"{humidity:.2f} %")

            mean_period = values['-MEAN-']
            if mean_period == '5 minut':
                mean_temp = avg_five_min_temperature
                mean_hum = avg_five_min_humidity
            elif mean_period == '30 minut':
                mean_temp = avg_thirty_min_temperature
                mean_hum = avg_thirty_min_humidity
            elif mean_period == '1 godziny':
                mean_temp = avg_hour_temperature
                mean_hum = avg_hour_humidity
            else:
                mean_temp = mean_hum = None

            homepage_window['-MEAN-TEMP-'].update(f"{mean_temp:.2f} C" if mean_temp is not None else "N/A")
            homepage_window['-MEAN-HUM-'].update(f"{mean_hum:.2f} %" if mean_hum is not None else "N/A")

            # Update status based on current flower selection
            current_flower = values['-FLOWER-']
            if current_flower in flower_preferences:
                pref_temp = flower_preferences[current_flower]['temp']
                pref_hum = flower_preferences[current_flower]['humidity']

                if pref_temp <= temperature <= pref_hum:
                    homepage_window['-STATUS-'].update(f"Twój kwiatek czuje się w porządku!")
                else:
                    homepage_window['-STATUS-'].update(f"Twój kwiatek nie czuje się dobrze!")


# Start the GUI update thread
gui_thread = Thread(target=update_gui)
gui_thread.daemon = True
gui_thread.start()

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

window.close()
homepage_window.close()
