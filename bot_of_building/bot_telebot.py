from telebot import TeleBot
from telebot.types import (
                           Message,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton
                           )
import os
from pathlib import Path
import datetime
import json
import db
from typing import List
from dotenv import load_dotenv
import re
import logging
from action_parse import get_info, get_weather

load_dotenv()

TOKEN = os.getenv("TOKEN")
WEATHER_KEY = os.getenv("WEATHERKEY")
BASE_DIR = Path(__file__).resolve().parent
JSON_SEND = BASE_DIR / "user_send.json"
DOCUMENT_FILES = BASE_DIR / "docs"
BELLS = DOCUMENT_FILES / "zvonki.txt"
DB_PATH = BASE_DIR / "db.db"
LOG_PATH = BASE_DIR / "logs.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s; [%(levelname)s] %(name)s: %(message)s\n",
    filename=LOG_PATH,
    encoding="utf-8"
)
logger = logging.getLogger(__name__)

bot = TeleBot(TOKEN)

state = {"starting": True}
# проверяем на существования файла user_send.json и открываем его.
if os.path.exists(JSON_SEND):
    with open(JSON_SEND, "r", encoding="utf-8") as s_file:
        send_data = json.load(s_file)
else:
    send_data = dict()
# открываем файл со звонками.
if os.path.exists(BELLS):
    with open(BELLS, "r", encoding="utf-8") as be_file:
        bells = be_file.read()
else:
    bells = None
# сохраняем данные в JSON файл.
def save_data(message, name_json, name_object):
    with open(name_json, "w", encoding="utf-8") as file:
        try:
            json.dump(name_object, file, ensure_ascii=False, indent=4)
        except Exception:
            bot.send_message(message.chat.id, "<i><b>Произошла ошибка при сохранении! Попробуй ещё раз♻️!</b></i>", parse_mode="HTML")
            logger.error("Ошибка при сохранении в JSON-файл!")
# список главных комманд.
def get_main_command() -> List[str]:
    return [
        "Личные данные💾",
        "Информацияℹ️",
        "Доп. функции✨",
        "Выход🚪"
    ]
# список комманд номер 1.
def get_command1() -> List[str]:
    return [
            "Профиль👤",
            "Время⌛",
            "Изменить возраст👴 и город🌃",
            "Выход🚪"
            ]
# список комманд номер 2.
def get_command2() -> List[str]:
    return [
        "Информация в DOCX-файле📋",
        "Отправить сообщение на адрес📩",
        "Получить информацию с сайтаℹ️",
        "Узнать погоду☔☀️",
        "Звонки🔔",
        "Выход🚪"
    ]
# проверяем на валидность адрес.
def valide_url(text : str) -> List[str]:
    return re.match(r"[a-zA-Z0-9\._%+-]+@[a-zA-Z0-9\.-]+\.(?:com|ru|by)", text)
# показываем список комманд.
@bot.message_handler(commands=["help"])
def help(message : Message):
    markup = InlineKeyboardMarkup()
    command = get_main_command()

    for s in command:
        markup.add(InlineKeyboardButton(s, callback_data=s))
    bot.send_message(message.chat.id, "<i><b>📋Список команд:</b></i>", parse_mode="HTML", reply_markup=markup)
# изменение возраста и города.
@bot.message_handler(commands=["set"])
def set(message: Message):
    text = message.text.split()

    try:
        age = text[1]
        city = str(text[2])
        db.set_age_city(message.from_user.id, age, city)

    except Exception:
        bot.send_message(message.chat.id, "<i><b>Возраст должен быть числом/Недостаточно аргументов в строке(Должно!!!: /set возраст город)!</b></i>", parse_mode="HTML")
        logger.error(f"{message.from_user.first_name} написал недостаточно аргументов/возраст не числом в функцию /set.")
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

        logger.info(f"Пользователь {message.from_user.first_name} решил отправить сообщение.")
# антиспам ссылок.
@bot.message_handler(chat_types=["private"], func=lambda m: m.entities is not None)
def delete_links(message : Message):
    for entity in message.entities:

        if entity.type in ("url", "text_link"):
            bot.delete_message(message.chat.id, message.message_id)
            break
# хендлер при входе пользователя.
@bot.message_handler()
def start(message : Message):
    if state["starting"]:
        if not os.path.exists(DB_PATH):
            db.create_table()

        bot.send_message(message.chat.id, f"<i><b>Добро пожаловать {message.from_user.first_name}🙌! Я бот, написанный на telebot\n</b></i>", parse_mode="HTML")
        state["starting"] = False

        if message.from_user.id in db.get_users_id():
            bot.send_message(message.chat.id, "<i><b>Вы вошли в профиль! Чтобы узнать список команд/повзаимодействовать со мной, нажми на /help</b></i>", parse_mode="HTML")
            return
        
        reg_date = datetime.datetime.now().date()
        parse_reg_date = datetime.datetime.strftime(reg_date, "%d.%m.%Y")

        db.insert_user(message.from_user.first_name, str(parse_reg_date), message.from_user.id)
        bot.send_message(message.chat.id, "<i><b>Я создал твой профиль по умолчанию, где есть только имя.\nЧтобы изменить профиль по умолчанию, нажми /help, после нажми на Изменить возраст и город, и там будет следуйщий шаг.</b></i>", parse_mode="HTML")
            
# обработчик событий.
@bot.callback_query_handler()
def action_for_keyboard(callback):
    main_command = get_main_command()
    command1 = get_command1()
    command2 = get_command2()

    if callback.data == main_command[0]:
        markup = InlineKeyboardMarkup()

        for s in command1:
            markup.add(InlineKeyboardButton(text=s, callback_data=s))
        bot.send_message(callback.message.chat.id, "<i><b>---Функции по личным данным💾---</b></i>", parse_mode="HTML", reply_markup=markup)

    elif callback.data == main_command[1]:
        markup = InlineKeyboardMarkup()

        for s in command2:
            markup.add(InlineKeyboardButton(text=s, callback_data=s))
        bot.send_message(callback.message.chat.id, "<i><b>---Информационные источникиℹ️---</b></i>", parse_mode="HTML", reply_markup=markup)

    elif callback.data == main_command[2]:
        bot.send_message(callback.message.chat.id, "<i><b>Функция на стадии разработки🛠️...</b></i>", parse_mode="HTML")

    elif callback.data == command1[0]:
        try:
            list_info = db.get_all_user_info(callback.from_user.id)

        except Exception:
            bot.send_message(callback.message.chat.id, "<i><b>У тебя нет данных!</b></i>", parse_mode="HTML")
            logger.error(f"У пользователя {callback.from_user.first_name} нет данных.")
        
        age = list_info[1]
        city = list_info[2]
        reg_date = list_info[3]

        bot.send_message(callback.message.chat.id, "<i><b>Твой профиль📇</b></i>\n"
                         f"<i><b>📛Имя: {callback.from_user.first_name}</b></i>\n"
                         f"<i><b>👴Возраст: {age}</b></i>\n"
                         f"<i><b>🌃Город: {city}</b></i>\n"
                         f"<i><b>🗓️Дата регестрации: {reg_date}</b></i>",
                         parse_mode="HTML"
                         )

    elif callback.data == command1[1]:
        now = datetime.datetime.now()
        parse_time = datetime.datetime.strftime(now, "%H:%M:%S")
        parse_date = datetime.datetime.strftime(now, "%d.%m.%Y")
        bot.send_message(callback.message.chat.id, f"<i><b>⌛Время сейчас: {parse_time}\n📆Дата: {parse_date}</b></i>", parse_mode="HTML")

    elif callback.data == command1[2]:
        bot.send_message(callback.message.chat.id, "<i><b>✍️Напиши на следующей строке /set возраст город(пример: /set 45 Париж)</b></i>", parse_mode="HTML")

    elif callback.data == command2[0]:
        try:
            with open(DOCUMENT_FILES / "doc.docx", "rb") as docx:
                bot.send_document(
                    callback.message.chat.id,
                    document=docx,
                    caption="DOCX файл⬆️"
                )
        except Exception:
            bot.send_message(callback.message.chat.id, "<i><b>Произошла ошибка! Возможно, что неккоректный путь/файл не существует.</b></i>")
            logger.error("Неккоректный путь или фалй не существует.")

    elif callback.data == command2[1]:
        bot.send_message(callback.message.chat.id, "<i><b>Напиши на следуйщей строке /send_text почта отправителя почта получателя текст. Пример:</b></i>", parse_mode="HTML")
        bot.send_message(callback.message.chat.id, "```/send_text vasyapupkin2@gmail.com(от кого) moidrug4@gmail.com(кому) Привет, дружище!```", parse_mode="Markdown")

    elif callback.data == command2[2]:
        info_site = get_info()[:10]
        parse_info = "\n".join(info_site)

        bot.send_message(callback.message.chat.id, f"<i><b>Информация с школьного сайта:\n{parse_info}</b></i>", parse_mode="HTML")
    
    elif callback.data == command2[3]:
        searching = get_weather(WEATHER_KEY)

        bot.send_message(callback.message.chat.id, searching, parse_mode="HTML")
    
    elif callback.data == command2[4]:
        
        if bells is not None:
            bot.send_message(callback.message.chat.id, f"<i><b>{bells}</b></i>", parse_mode="HTML")
        else:
            bot.send_message(callback.message.chat.id, "<i><b>Расписания звонков пока ещё нет!</b></i>", parse_mode="HTML")

    elif callback.data == main_command[3]:
        bot.edit_message_reply_markup(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=None
                )

        bot.delete_message(callback.message.chat.id, callback.message.message_id)

bot.infinity_polling(skip_pending=True)