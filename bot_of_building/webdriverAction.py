from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
import requests
from time import sleep
from typing import List

options = webdriver.EdgeOptions()

options.add_argument("headless")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36")
options.add_argument("--window-size=1920,1080")
options.add_argument("--lang=ru-RU")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

def get_element() -> List[str]:

    driver = webdriver.Edge(options=options)

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    list_element = list()

    url = "https://maxim-programmer12.github.io/myHTML-document/"

    try:
        driver.get(url)

    except InvalidArgumentException:
        print("Произошла ошибка!\nНеправильный url-адрес.")

    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//p[1]"))).text
    list_element.append(element)

    for i in range(2, 5):
        try:
            element = driver.find_element(By.XPATH, f"//p[{i}]").text
            list_element.append(element)

        except NoSuchElementException:
            list_element.append(f"Элемента под номером {i} нет!")

    driver.close()
    driver.quit()

    return list_element

def get_weather(city : str, weather_api_key : str) -> str:

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&lang=ru&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return "<i><b>Не найден город!</b></i>"
    
    data = response.json()

    name = data["name"]
    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]
    hum = data["main"]["humidity"]
    desc = data["weather"][0]["description"]
    icon = data["weather"][0]["icon"]

    return (
        f'<i><b>Погода в городе {name} {icon}:</b></i>\n'
        f'<i><b>Температура: {temp}C° </b></i>\n'
        f'<i><b>Ощущается как: {feels}C° </b></i>\n'
        f'<i><b>Влажность: {hum}%\n</b></i>'
        f'<i><b>Погодное условие: {desc.capitalize()}</b></i>'
    )