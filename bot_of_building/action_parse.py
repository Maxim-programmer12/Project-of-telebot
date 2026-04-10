from typing import List
from pathlib import Path
# константы.
BASE_DIR = Path(__file__).resolve().parent
FONT_FILE = BASE_DIR / "Roboto-VariableFont_wdth,wght.ttf"
# Информация с сайта СШ №1 г. Пружаны.
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
# погода в городе Пружаны.
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
# отрисовка искажения текста.
def wave_distortion(img, amplitude=5, wavelength=30):
    from PIL import Image
    import math

    w, h = img.size

    new = Image.new("RGB", (w, h), "white")

    pixels_new = new.load()
    pixels_old = img.load()

    for x in range(w):
        for y in range(h):
            offset = int(amplitude * math.sin(2 * math.pi * y / wavelength))
            new_x = x + offset

            if 0 <= new_x < w:
                pixels_new[new_x, y] = pixels_old[x, y]

    return new
# генерация карточки для CAPTCHA.
def generate_card(text : str, message):
    from PIL import Image, ImageDraw, ImageFont
    from random import randint

    bg = (
        randint(0, 255),
        randint(0, 255),
        randint(0, 255)
    )

    img = Image.new("RGB", (400, 250), bg)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_FILE, 100)

    bbox = draw.textbbox((0, 0), text, font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (img.width - w) // 2
    y = (img.height - h) // 2

    draw.text((x, y), text, font=font, fill="black")

    for _ in range(300):
        x = randint(0, img.width)
        y = randint(0, img.height)

        draw.point((x, y), fill=(randint(0, 255) * 3))

    img = wave_distortion(img)
    img.save(BASE_DIR / f"card_captcha{message.from_user.id}.png")

if __name__ == "__main__":
    # generate_card("87653", 5)
    """list_p = get_info()
    print(list_p)"""
    pass