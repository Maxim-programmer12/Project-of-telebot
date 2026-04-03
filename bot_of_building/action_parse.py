from typing import List

def get_info() -> List[str]:
    import requests
    from bs4 import BeautifulSoup

    url = "https://school1.pruzhany.by/category/novosti/"

    res = requests.get(url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")

    div = soup.find("div", id="blog-entries")

    ps = div.find_all("p")

    return [p.text for p in ps]

def get_weather(weather_api_key : str) -> str:
    import requests

    url = f"https://api.openweathermap.org/data/2.5/weather?q=Pruzhany&appid={weather_api_key}&lang=ru&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return "<i><b>Произошла ошибка при запросе!</b></i>"
    
    data = response.json()

    name = data["name"]
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    hum = data["main"]["humidity"]
    desc = data["weather"][0]["description"]
    icon = data["weather"][0]["icon"]

    return (
        f'<i><b>Погода в городе {name} {icon}</b></i>\n'
        f'<i><b>Температура: {temp}C° </b></i>\n'
        f'<i><b>Ощущается как: {feels}C° </b></i>\n'
        f'<i><b>Влажность: {hum}%\n</b></i>'
        f'<i><b>Погодное условие: {desc.capitalize()}</b></i>'
    )

if __name__ == "__main__":
    pass
    list_p = get_info()
    print(list_p)