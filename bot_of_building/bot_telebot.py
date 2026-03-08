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

load_dotenv()

TOKEN = os.getenv("TOKEN_ANYbot")
BASE_DIR = Path(__file__).resolve().parent
JSON_USERS = BASE_DIR / "users_profile.json"
DOCUMENT_FILES = BASE_DIR / "docs"

bot = TeleBot(TOKEN)
state = {"starting": True}

if os.path.exists(JSON_USERS):
    with open(JSON_USERS, "r", encoding="utf-8") as file:
        json_data = json.load(file)
else:
    json_data = {}

def save_data(message):
    with open(JSON_USERS, "w", encoding="utf-8") as file:
        try:
            json.dump(json_data, file, ensure_ascii=False, indent=4)
        except Exception:
            bot.send_message(message.chat.id, "<i><b>Произошла ошибка при сохранении! Попробуй ещё раз♻️!</b></i>", parse_mode="HTML")

def get_command() -> List:
    return ["Приветствие🙌", "Профиль👤", "Время⌛", "Изменить возраст👴 и город🌃", "Получить ежедневную награду💲", "Обменник коинов💱", "Информация в DOCX📋", "Отправить сообщение на адрес📧", "Выход🚪"]

def get_shop_items() -> List:
    return [
        {"name": "VIP🤑", "price": 500},
        {"name": "Photo📸", "price": 50}
    ]

def return_shop_items() -> Dict: 
    return {items["name"]: items["price"] for items in get_shop_items()}

def valide_url(text : str) -> List:
    return re.findall(r"[a-zA-Z0-9_@+-]+@[a-zA-Z0-9_+-]+\.(com|ru|by)", text)

@bot.message_handler(commands=["help"])
def help(message : Message):
    markup = InlineKeyboardMarkup()
    command = get_command()
    for s in command:
        markup.add(InlineKeyboardButton(s, callback_data=s))
    bot.send_message(message.chat.id, "<i><b>📋Список команд:</b></i>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=["set"])
def set(message: Message):
    text = message.text.split()

    try:
        json_data[str(message.from_user.id)]["age"] = int(text[1]); json_data[str(message.from_user.id)]["city"] = text[2].title()
        save_data(message)

    except Exception:
        bot.send_message(message.chat.id, "<i><b>Возраст должен быть числом/Недостаточно аргументов в строке(Должно!!!: /set возраст город)!</b></i>", parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "<i><b>Успешно изменён профиль!</b></i>", parse_mode="HTML")

@bot.message_handler(commands=["send_text"])
def send_text(message : Message):
    text = message.text.split()

    if len(text) < 4:
        bot.send_message(message.chat.id, "<i><b>Недостаточно аргументов в строке! Надо так(пример):\n/send_text vasyapupkin2@gmail.com moidrug4@gmail.com Привет, дружище!</b></i>", parse_mode="HTML")
    else:
        seacrh_url = valide_url(f"{text[1]} {text[2]}")
        seacrh_text = " ".join(text[3:])

        if len(seacrh_url) < 2:
            bot.send_message(message.chat.id, "<i><b>Невалидный(-ые) адрес(-а) эл. почты! Попробуй заново ввести по шаблону(/send_text vasyapupkin2@gmail.com moidrug4@gmail.com Привет, дружище!)ю</b></i>", parse_mode="HTML")

@bot.message_handler()
def start(message : Message):
    if state["starting"]:
        bot.send_message(message.chat.id, f"<i><b>Добро пожаловать {message.from_user.first_name}🙌! Я бот, написанный на telebot\n</b></i>", parse_mode="HTML")
        state["starting"] = False

        if str(message.from_user.id) in json_data:
            bot.send_message(message.chat.id, "<i><b>Вы вошли в профиль! Чтобы узнать список команд/повзаимодействовать со мной, нажми на /help</b></i>", parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "<i><b>Я создал твой профиль по умолчанию, где есть только имя.\nЧтобы изменить профиль по умолчанию, нажми /help, после нажми на Изменить возраст и город, и там будет следуйщий шаг.</b></i>", parse_mode="HTML")

            json_data[str(message.from_user.id)] = {"name": message.from_user.first_name, "age": "не указан", "city": "не указан", "last_daily": str(datetime.datetime.now().date()), "coins": 0, "inventory": []}
            save_data(message)

@bot.callback_query_handler()
def action_for_keyboard(callback):
    command = get_command()

    if callback.data == command[0]:
        bot.send_message(callback.message.chat.id, f"<i><b>Приветствую🙌, {callback.from_user.first_name}! Я бот, написанный на telebot.</b></i>", parse_mode="HTML")

    elif callback.data == command[1]:
        try:
            user = json_data[str(callback.from_user.id)]
            name = user["name"]
            age = user["age"]
            city = user["city"]
            coins = user["coins"]

        except Exception:
            bot.send_message(callback.message.chat.id, "<i><b>У тебя нет данных!</b></i>", parse_mode="HTML")
            return

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
        user = json_data[str(callback.from_user.id)]
        date_now = str(datetime.datetime.now().date())

        if user["last_daily"] == date_now:
            bot.send_message(callback.message.chat.id, "<i><b>Ты уже получал награду💸, заходи завтра!</b></i>", parse_mode="HTML")
        else:
            coins = 150 if "VIP🤑" in user["inventory"] else 50

            user["coins"] += coins
            user["last_daily"] = date_now
            save_data(callback.message)

            bot.send_message(callback.message.chat.id, f"<i><b>Ты получил ежедневку: {coins} коинов💲!</b></i>", parse_mode="HTML")

    elif callback.data == command[5]:
        markup = InlineKeyboardMarkup()

        for item in get_shop_items():
            markup.add(InlineKeyboardButton(text=f"{item['name']} - {item['price']}", callback_data=item["name"]))
        markup.add(InlineKeyboardButton("Выход🚪", callback_data="Выйти"))

        bot.send_message(callback.message.chat.id, "<i><b>Добро пожаловать в магазин🙌! Тут продаётся:</b></i>", parse_mode="HTML", reply_markup=markup)
    
    elif callback.data in return_shop_items():
        user = json_data[str(callback.from_user.id)]
        shop_items = return_shop_items()

        if callback.data in shop_items:
            item_price = shop_items[callback.data]

            if user["coins"] >= item_price and callback.data not in user["inventory"]:
                user["coins"] -= item_price
                user["inventory"].append(callback.data)
                save_data(callback.message)

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

    elif callback.data == "Выйти":
        bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )

        bot.delete_message(callback.message.chat.id, callback.message.message_id)

    elif callback.data == command[8]:
        bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=None
                )

        bot.delete_message(callback.message.chat.id, callback.message.message_id)

bot.polling(non_stop=True)