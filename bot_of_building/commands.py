import datetime
import db
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from action_parse import get_info, get_weather
from object_bot import object_bot
# загружаем данные из .env .
load_dotenv()
# константы.
WEATHER_KEY = os.getenv("WEATHERKEY")
BASE_DIR = Path(__file__).resolve().parent
DOCUMENT_FILES = BASE_DIR / "docs"
BELLS = DOCUMENT_FILES / "zvonki.txt"
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
# открываем файл со звонками.
if os.path.exists(BELLS):
    with open(BELLS, "r", encoding="utf-8") as be_file:
        bells = be_file.read()
else:
    bells = None
# получение информации о пользователе.
def get_user_info(callback):
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
# получение даты.
def get_date(callback):
    now = datetime.datetime.now()
    parse_time = datetime.datetime.strftime(now, "%H:%M:%S")
    parse_date = datetime.datetime.strftime(now, "%d.%m.%Y")
    bot.send_message(callback.message.chat.id, f"<i><b>⌛Время сейчас: {parse_time}\n📆Дата: {parse_date}</b></i>", parse_mode="HTML")
# изменение возраста и города.
def set_info(callback):
    bot.send_message(callback.message.chat.id, "<i><b>✍️Напиши на следующей строке /set возраст город(пример: /set 45 Париж)</b></i>", parse_mode="HTML")
# отправка DOCX-файла.
def send_doc(callback):
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
# отправка текста на почту.
def send_mail(callback):
    bot.send_message(callback.message.chat.id, "<i><b>Напиши на следуйщей строке /send_text почта отправителя почта получателя текст. Пример:</b></i>", parse_mode="HTML")
    bot.send_message(callback.message.chat.id, "```/send_text vasyapupkin2@gmail.com(от кого) moidrug4@gmail.com(кому) Привет, дружище!```", parse_mode="Markdown")
# получение информации с сайта.
def get_info_site(callback):
    info_site = get_info()[:10]

    if len(info_site) < 1:
        bot.send_message(callback.message.chat.id, "<i><b></b></i>", parse_mode="HTML")
        
    parse_info = "\n".join(info_site)

    bot.send_message(callback.message.chat.id, f"<i><b>ℹ️Информация с школьного сайта(последние {len(info_site)} заголовков(-а)):\n{parse_info}</b></i>", parse_mode="HTML")
# отправка погоды.
def send_weather(callback):
    searching = get_weather(WEATHER_KEY)

    bot.send_message(callback.message.chat.id, searching, parse_mode="HTML")
# отправка звонков.
def send_bells(callback):        
    if bells is not None:
            bot.send_message(callback.message.chat.id, f"<i><b>{bells}</b></i>", parse_mode="HTML")
    else:
        bot.send_message(callback.message.chat.id, "<i><b>Расписания звонков пока ещё нет!❌</b></i>", parse_mode="HTML")
# удаление клавиатуры.
def delete_keyboard(callback):
    bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None
            )

    bot.delete_message(callback.message.chat.id, callback.message.message_id)