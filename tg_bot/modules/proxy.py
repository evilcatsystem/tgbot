from bs4 import BeautifulSoup
import requests

from telegram import Update, Bot
from telegram.ext import CommandHandler
from tg_bot.modules.sql.top_users_sql import protected
from tg_bot import dispatcher

def proxy(bot: Bot, update: Update):
    user = update.effective_user  
    user_id = user.id
    if protected(user_id):
        update.effective_message.delete()
        url = requests.get('https://us-proxy.org/')
        soup = BeautifulSoup(url.text, features="lxml")
        text = soup.find('textarea', class_='form-control')

        FILE = open ("tg_bot/modules/proxy_list", "r+")
        print (text, file = FILE)
        FILE.close()

        with open("tg_bot/modules/proxy_list", "rb") as file:
            chat = update.effective_chat
            bot.send_document(chat.id, document=file, filename='proxy.txt')

__help__ = "/proxy - Получить список прокси"

__mod_name__ = "Proxy"


BROADCAST_HANDLER = CommandHandler("proxy", proxy)
dispatcher.add_handler(BROADCAST_HANDLER)
