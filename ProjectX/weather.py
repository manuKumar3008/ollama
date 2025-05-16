import ollama
import requests

OPENWEATHER_API_KEY = 'f65972143e13314171a62e07cd3b5e2c'  # Replace with your key
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'

def get_weather(city):
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric'
    }
    response = requests.get(WEATHER_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return f"The current temperature in {city} is {temp}°C with {desc}."
    else:
        return "Sorry, I couldn't fetch the weather for that city."

def is_weather_question(question):
    response = ollama.chat(model='llama3.2', messages=[
        {'role': 'system', 'content': 'Return only "yes" if the user is asking about current weather, otherwise return "no".'},
        {'role': 'user', 'content': question}
    ])
    return 'yes' in response['message']['content'].lower()

def extract_city_name(question):
    response = ollama.chat(model='llama3.2', messages=[
        {'role': 'system', 'content': 'Extract the city name from this weather-related question and return only the city name.'},
        {'role': 'user', 'content': question}
    ])
    return response['message']['content'].strip()

# Main loop
while True:
    user_input = input("You: ")

    if is_weather_question(user_input):
        city = extract_city_name(user_input)
        print("Fetching weather for:", city)
        weather_info = get_weather(city)
        print("Assistant:", weather_info)
    else:
        response = ollama.chat(model='llama3.2', messages=[
            {'role': 'user', 'content': user_input}
        ])
        print("Assistant:", response['message']['content'])
