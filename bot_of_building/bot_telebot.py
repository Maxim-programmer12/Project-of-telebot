from telebot import TeleBot
from telebot.types import (
                           Message,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardMarkup,
                           ReplyKeyboardRemove,
                           KeyboardButton
                           )
import os
from pathlib import Path
import datetime
import json
from time import sleep
from typing import List, Dict
from dotenv import load_dotenv
import re
from action_parse import get_element, get_weather

load_dotenv()

TOKEN = os.getenv("TOKEN_ANYbot")
WEATHER_KEY = os.getenv("WEATHERKEY")
BASE_DIR = Path(__file__).resolve().parent
JSON_USERS = BASE_DIR / "users_profile.json"
JSON_SEND = BASE_DIR / "user_send.json"
DOCUMENT_FILES = BASE_DIR / "docs"

bot = TeleBot(TOKEN)

action_Element = get_element()

state = {"starting": True}
# проверяем на существования файла user_profile.json и открываем его.
if os.path.exists(JSON_USERS):
    with open(JSON_USERS, "r", encoding="utf-8") as u_file:
        user_data = json.load(u_file)
else:
    user_data = dict()
# проверяем на существования файла user_send.json и открываем его.
if os.path.exists(JSON_SEND):
    with open(JSON_SEND, "r", encoding="utf-8") as s_file:
        send_data = json.load(s_file)
else:
    send_data = dict()
# сохраняем данные в JSON файл.
def save_data(message, name_json, name_object):
    with open(name_json, "w", encoding="utf-8") as file:
        try:
            json.dump(name_object, file, ensure_ascii=False, indent=4)
        except Exception:
            bot.send_message(message.chat.id, "<i><b>Произошла ошибка при сохранении! Попробуй ещё раз♻️!</b></i>", parse_mode="HTML")
# список комманд.
def get_command() -> List[str]:
    return [
            "Приветствие🙌", 
            "Профиль👤", 
            "Время⌛", 
            "Изменить возраст👴 и город🌃", 
            "Получить ежедневную награду💲", 
            "Обменник коинов💱", 
            "Информация в DOCX📋", 
            "Отправить сообщение на адрес📧",
            "Получить информацию с сайтаℹ️",
            "Узнать погоду☔☀️",
            "Выход🚪"
            ]
# предметы обменника коинов.
def get_shop_items() -> List:
    return [
        {"name": "VIP🤑", "price": 500},
        {"name": "Photo📸", "price": 50}
    ]
# возвращаем название предмета и его стоимость через генератор словарей.
def return_shop_items() -> Dict: 
    return {items["name"]: items["price"] for items in get_shop_items()}
# проверяем на валидность адрес.
def valide_url(text : str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9\._%+-]+@[a-zA-Z0-9\.-]+\.(?:com|ru|by)", text)
# показываем список комманд.
@bot.message_handler(commands=["help"])
def help(message : Message):
    markup = InlineKeyboardMarkup()
    command = get_command()
    for s in command:
        markup.add(InlineKeyboardButton(s, callback_data=s))
    bot.send_message(message.chat.id, "<i><b>📋Список команд:</b></i>", parse_mode="HTML", reply_markup=markup)
# антиспам ссылок.
@bot.message_handler(chat_types=["private"], func=lambda m: m.entities is not None)
def delete_links(message : Message):
    for entity in message.entities:

        if entity.type in ("url", "text_link"):
            bot.delete_message(message.chat.id, message.message_id)
            break
# показ прогноза погоды.
@bot.message_handler(commands=["weather"])
def weather(message : Message):
    text = message.text.split(" ")

    if len(text) < 2:
        bot.send_message(message.chat.id, "Недостаточно аргументов в строке! Надо так: ```\n/weather название города```", parse_mode="Markdown")
        return

    seacrhing = get_weather(*text[1:], WEATHER_KEY)

    bot.send_message(message.chat.id, seacrhing, parse_mode="HTML")
# изменение возраста и города.
@bot.message_handler(commands=["set"])
def set(message: Message):
    text = message.text.split()

    try:
        user_data[str(message.from_user.id)]["age"] = int(text[1]); user_data[str(message.from_user.id)]["city"] = text[2].title()
        save_data(message, JSON_USERS, user_data)

    except Exception:
        bot.send_message(message.chat.id, "<i><b>Возраст должен быть числом/Недостаточно аргументов в строке(Должно!!!: /set возраст город)!</b></i>", parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "<i><b>Успешно изменён профиль!</b></i>", parse_mode="HTML")
# сбор и отправка через эл. почту форму.
@bot.message_handler(commands=["send_text"])
def send_text(message : Message):
    text = message.text.split()

    if len(text) < 4:
        bot.send_message(message.chat.id, "<i><b>Недостаточно аргументов в строке! Надо так(пример):\n/send_text vasyapupkin2@gmail.com(от кого) moidrug4@gmail.com(кому) Привет, дружище!</b></i>", parse_mode="HTML")
    else:
        search_text = " ".join(text[3:])
        url_sender = text[1]
        url_getter = text[2]

        if not valide_url(url_sender) or not valide_url(url_getter):
            bot.send_message(message.chat.id, "<i><b>❌Невалидный адрес отправителя/получателя!\n"
                             "Попробуй отправить заново.</b></i>",
                             parse_mode="HTML")
            return
        
        send_data[str(message.from_user.id)] = {
            "from": url_sender,
            "to": url_getter,
            "text": search_text,
            "ready": True
        }
        save_data(message, JSON_SEND, send_data)
# хендлер при входе пользователя.
@bot.message_handler()
def start(message : Message):
    if state["starting"]:
        bot.send_message(message.chat.id, f"<i><b>Добро пожаловать {message.from_user.first_name}🙌! Я бот, написанный на telebot\n</b></i>", parse_mode="HTML")
        state["starting"] = False

        if str(message.from_user.id) in user_data:
            bot.send_message(message.chat.id, "<i><b>Вы вошли в профиль! Чтобы узнать список команд/повзаимодействовать со мной, нажми на /help</b></i>", parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "<i><b>Я создал твой профиль по умолчанию, где есть только имя.\nЧтобы изменить профиль по умолчанию, нажми /help, после нажми на Изменить возраст и город, и там будет следуйщий шаг.</b></i>", parse_mode="HTML")

            user_data[str(message.from_user.id)] = {"name": message.from_user.first_name, "age": "не указан", "city": "не указан", "last_daily": str(datetime.datetime.now().date()), "coins": 0, "inventory": []}
            save_data(message, JSON_USERS, user_data)
# обработчик событий.
@bot.callback_query_handler()
def action_for_keyboard(callback):
    command = get_command()

    if callback.data == command[0]:
        bot.send_message(callback.message.chat.id, f"<i><b>Приветствую🙌, {callback.from_user.first_name}! Я бот, написанный на telebot.</b></i>", parse_mode="HTML")

    elif callback.data == command[1]:
        try:
            user = user_data[str(callback.from_user.id)]
            name = user["name"]
            age = user["age"]
            city = user["city"]
            coins = user["coins"]

        except Exception:
            bot.send_message(callback.message.chat.id, "<i><b>У тебя нет данных!</b></i>", parse_mode="HTML")

        bot.send_message(callback.message.chat.id, "<i><b>Твой профиль📇</b></i>\n"
                         f"<i><b>📛Имя: {name}</b></i>\n"
                         f"<i><b>👴Возраст: {age}</b></i>\n"
                         f"<i><b>🌃Город: {city}</b></i>\n"
                         f"<i><b>🪙Коины: {coins}</b></i>",
                         parse_mode="HTML"
                         )

    elif callback.data == command[2]:
        now = datetime.datetime.now()
        parse_time = datetime.datetime.strftime(now, "%H:%M:%S")
        parse_date = datetime.datetime.strftime(now, "%d.%m.%Y")
        bot.send_message(callback.message.chat.id, f"<i><b>⌛Время сейчас: {parse_time}\n📆Дата: {parse_date}</b></i>", parse_mode="HTML")

    elif callback.data == command[3]:
        bot.send_message(callback.message.chat.id, "<i><b>✍️Напиши на следуйщей строке /set возраст город(пример: /set 45 Париж)</b></i>", parse_mode="HTML")

    elif callback.data == command[4]:
        user = user_data[str(callback.from_user.id)]
        date_now = str(datetime.datetime.now().date())

        if user["last_daily"] == date_now:
            bot.send_message(callback.message.chat.id, "<i><b>Ты уже получал награду💸, заходи завтра!</b></i>", parse_mode="HTML")
        else:
            coins = 150 if "VIP🤑" in user["inventory"] else 50

            user["coins"] += coins
            user["last_daily"] = date_now
            save_data(callback.message, JSON_USERS, user_data)

            bot.send_message(callback.message.chat.id, f"<i><b>Ты получил ежедневку: {coins} коинов💲!</b></i>", parse_mode="HTML")

    elif callback.data == command[5]:
        markup = InlineKeyboardMarkup()

        for item in get_shop_items():
            markup.add(InlineKeyboardButton(text=f"{item['name']} - {item['price']}", callback_data=item["name"]))
        markup.add(InlineKeyboardButton("Выход🚪", callback_data="Выйти"))

        bot.send_message(callback.message.chat.id, "<i><b>Добро пожаловать в магазин🙌! Тут продаётся:</b></i>", parse_mode="HTML", reply_markup=markup)
    
    elif callback.data in return_shop_items():
        user = user_data[str(callback.from_user.id)]
        shop_items = return_shop_items()

        if callback.data in shop_items:
            item_price = shop_items[callback.data]

            if user["coins"] >= item_price and callback.data not in user["inventory"]:
                user["coins"] -= item_price
                user["inventory"].append(callback.data)
                save_data(callback.message, JSON_USERS, user_data)

                if callback.data == "Photo📸" and "Photo📸" not in user["inventory"]:
                    try:
                        with open(DOCUMENT_FILES / "photo.jpg", "rb") as photo:
                            bot.send_photo(
                                callback.message.chat.id,
                                photo=photo,
                                caption="ФОТО за 50 коинов⬆️"
                            )
                    except Exception:
                        bot.send_message(callback.message.chat.id, "<i><b>Произошла ошибка! Файл не найден/некорректный путь.</b></i>", parse_mode="HTML")

                bot.send_message(callback.message.chat.id, f"<i><b>Успешно приобретён {callback.data} за {item_price} коинов(-а)!</b></i>", parse_mode="HTML")

            elif callback.data in user["inventory"]:
                bot.send_message(callback.message.chat.id, f"<i><b>У тебя этот предмет есть!</b></i>", parse_mode="HTML")
            else:
                bot.send_message(callback.message.chat.id, "<i><b>Не хватает коинов!</b></i>", parse_mode="HTML")
    
    elif callback.data == command[6]:
        try:
            with open(DOCUMENT_FILES / "doc.docx", "rb") as docx:
                bot.send_document(
                    callback.message.chat.id,
                    document=docx,
                    caption="DOCX файл⬆️"
                )
        except Exception:
            bot.send_message(callback.message.chat.id, "<i><b>Произошла ошибка! Возможно, что неккоректный путь/файл не существует.</b></i>")

    elif callback.data == command[7]:
        bot.send_message(callback.message.chat.id, "<i><b>Напиши на следуйщей строке команду /send_text, свой адрес, адрес получателя и текст получателю(пример:/send_text vasyapupkin2@gmail.com moidrug4@gmail.com Привет, дружище!)</b></i>", parse_mode="HTML")

    elif callback.data == command[8]:
        if action_Element is None:
            bot.send_message(callback.message.chat.id, f"<i><b>Ещё загружаю элементы...</b></i>", parse_mode="HTML")
        else:
            bot.send_message(callback.message.chat.id, f"<i><b>{'\n'.join(action_Element)}</b></i>", parse_mode="HTML")

    elif callback.data == command[9]:
        bot.send_message(callback.message.chat.id, "<i><b>Напиши на следуйщей строке /weather название города(например: /weather Moscov)</b></i>", parse_mode="HTML")

    elif callback.data == "Выйти":
        bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )

        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == command[10]:
        bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=None
                )

        bot.delete_message(callback.message.chat.id, callback.message.message_id)

bot.polling(non_stop=True)