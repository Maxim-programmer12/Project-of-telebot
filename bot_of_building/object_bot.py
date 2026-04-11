from telebot import TeleBot
import os
from dotenv import load_dotenv
# загружаем данные из .env .
load_dotenv()
# константы.
TOKEN = os.getenv("TOKEN")
# объект TeleBot.
bot = TeleBot(TOKEN)
# возвращаем объект bot.
def object_bot() -> TeleBot:
    return bot

if __name__ == "__main__":
    # print(object_bot())
    pass