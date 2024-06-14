#import projekt as pk

# Storczyk T: 18-24 >15   W:50-70
# Pieniążek T: 18-24  nagle zle  W: 40-50
# Monstera T: 20-30 >13 W: 60-80
# Fikus T: 18-24 >15   W: 40-60

def get_plant_requirements(plant_name):
    if plant_name == 'Storczyk':
        temperature = "18-24°C (dzień), 16-18°C (noc)"
        humidity = "50-70%"
    elif plant_name == 'Pieniążek':
        temperature = "18-24°C"
        humidity = "40-50%"
    elif plant_name == 'Monstera':
        temperature = "20-30°C"
        humidity = "60-80%"
    elif plant_name == 'Fikus':
        temperature = "18-24°C"
        humidity = "40-60%"
    else:
        temperature = "Nieznana"
        humidity = "Nieznana"

    return temperature, humidity


# Przykład użycia
plant_name = 'Storczyk'  # Możesz podać dowolną nazwę rośliny z listy: 'Storczyk', 'Pieniążek', 'Monstera', 'Fikus'
temperature, humidity = get_plant_requirements(plant_name)
print(f"Wymagania dla {plant_name}:")
print(f"Temperatura: {temperature}")
print(f"Wilgotność: {humidity}")


