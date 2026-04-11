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
from typing import List, Dict, Callable
from dotenv import load_dotenv
import logging
from action_parse import generate_card, valide_url
from random import randint
from commands import (
    get_user_info,
    get_date,
    get_info_site,
    send_bells,
    send_doc,
    send_mail,
    send_weather,
    set_info,
    delete_keyboard
)
from object_bot import object_bot
# загружаем данные из .env .
load_dotenv()
# константы.
BASE_DIR = Path(__file__).resolve().parent
JSON_SEND = BASE_DIR / "user_send.json"
DB_PATH = BASE_DIR / "db.db"
LOG_PATH = BASE_DIR / "logs.log"
# логирование.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s; [%(levelname)s] %(name)s: %(message)s\n",
    filename=LOG_PATH,
    encoding="utf-8"
)
logger = logging.getLogger(__name__)
# объект TeleBot.
bot = object_bot()
# статусы.
state = {"starting": True}
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
            logger.error("Ошибка при сохранении в JSON-файл!")
# список главных комманд.
def get_main_command() -> List[str]:
    return [
        "Личные данные💾",
        "Информацияℹ️",
        "Доп. функции✨",
        "Скрыть🚪"
    ]
# список комманд номер 1.
def get_command1() -> List[str]:
    return [
            "Профиль👤",
            "Время⌛",
            "Изменить возраст👴 и город🌃",
            "Скрыть🚪"
            ]
# список комманд номер 2.
def get_command2() -> List[str]:
    return [
        "Информация в DOCX-файле📋",
        "Отправить сообщение на адрес📩",
        "Получить информацию с сайтаℹ️",
        "Узнать погоду☔☀️",
        "Звонки🔔",
        "Скрыть🚪"
    ]
# создание 1-ой клавиатуры.
def make_keyboard1(callback):
    markup = InlineKeyboardMarkup()

    for s in get_command1():
        markup.add(InlineKeyboardButton(text=s, callback_data=s, style="danger"))
    bot.send_message(callback.message.chat.id, "<i><b>---Функции по личным данным💾---</b></i>", parse_mode="HTML", reply_markup=markup)
# создание 2-ой клавиатуры.
def make_keyboard2(callback):
    markup = InlineKeyboardMarkup()

    for s in get_command2():
        markup.add(InlineKeyboardButton(text=s, callback_data=s, style="primary"))
    bot.send_message(callback.message.chat.id, "<i><b>---Информационные источникиℹ️---</b></i>", parse_mode="HTML", reply_markup=markup)
# создание 3-ей клавиатуры.
def make_keyboard3(callback):
    bot.send_message(callback.message.chat.id, "<i><b>Функция на стадии разработки🛠️...</b></i>", parse_mode="HTML")
# все комманды и их функции.
def all_commands() -> Dict[str, Callable]:
    return {
        # Главное меню
        "Личные данные💾": make_keyboard1,
        "Информацияℹ️": make_keyboard2,
        "Доп. функции✨": make_keyboard3,
        "Скрыть🚪": delete_keyboard,

        # Команды №1
        "Профиль👤": get_user_info,
        "Время⌛": get_date,
        "Изменить возраст👴 и город🌃": set_info,

        # Команды №2
        "Информация в DOCX-файле📋": send_doc,
        "Отправить сообщение на адрес📩": send_mail,
        "Получить информацию с сайтаℹ️": get_info_site,
        "Узнать погоду☔☀️": send_weather,
        "Звонки🔔": send_bells,
    }
# показываем список комманд.
@bot.message_handler(commands=["help"])
def help(message : Message):
    if db.get_info_captcha(message.from_user.id)[0] != 1:
        markup = InlineKeyboardMarkup()
        command = get_main_command()

        for s in command:
            markup.add(InlineKeyboardButton(s, callback_data=s, style="success"))
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

        r_numb = randint(11111, 99999)

        generate_card(str(r_numb), message)

        reg_date = datetime.datetime.now().date()
        parse_reg_date = datetime.datetime.strftime(reg_date, "%d.%m.%Y")

        db.insert_user(message.from_user.first_name, str(parse_reg_date), message.from_user.id)
        db.set_state_captcha(message.from_user.id, r_numb, 1)
        
        with open(BASE_DIR / f"card_captcha{message.from_user.id}.png", "rb") as captcha:
            bot.send_photo(message.chat.id, 
                           photo=captcha, 
                           caption="<i><b>CAPTCHA-проверка:\nнапиши число, которое видешь на изображении.</b></i>", 
                           parse_mode="HTML")
    
    if db.get_info_captcha(message.from_user.id)[0] == 1:
        text = message.text

        if text == str(db.get_info_captcha(message.from_user.id)[1]):
            bot.send_message(message.chat.id, "<i><b>Правильно! Доступ разрешён✅.</b></i>", parse_mode="HTML")

            db.set_state_captcha(message.from_user.id, 0, 0)

            if message.from_user.id in db.get_users_id():
                bot.send_message(message.chat.id, "<i><b>Вы вошли в профиль! Чтобы узнать список команд/повзаимодействовать со мной, нажми на /help</b></i>", parse_mode="HTML")
                return
# обработчик событий.
@bot.callback_query_handler()
def action_for_keyboard(callback):
    handle = all_commands().get(callback.data)

    if handle:
        handle(callback)
    else:
        logger.error(f"{callback.from_user.first_name} нажал несуществующую кнопку.")

bot.infinity_polling(skip_pending=True)