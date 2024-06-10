import PySimpleGUI as sg

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
        event, values = homepage_window.read()

        if event == sg.WIN_CLOSED:
            homepage_active = False
            break

window.close()
homepage_window.close()
