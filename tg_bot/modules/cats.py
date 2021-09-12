import requests
from bs4 import BeautifulSoup

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackQueryHandler

from tg_bot import dispatcher

def cats(bot: Bot, update: Update):
    user_agent = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }

    search = "https://theoldreader.com/kittens/1366/768/js" #Запрашиваем у юзера, что он хочет найти
    url = requests.get(search, headers=user_agent) #Делаем запрос
    soup = BeautifulSoup(url.text, features="lxml") #Получаем запрос
    result = soup.find("img").get("src") #Ищем тег <img src="ссылка.png"
    result = "https://theoldreader.com" + result
    chat = update.effective_chat
    cat = [
                [   
                    InlineKeyboardButton('Еще хочу котейку', callback_data='cat_more'),
                    InlineKeyboardButton('❌', callback_data='top_delete_message')
                ]
            ]
    reply_markup = InlineKeyboardMarkup(cat)
    bot.send_photo(chat.id,photo=result, reply_markup=reply_markup, parse_mode= "Markdown")

def cat_button(bot: Bot, update: Update):
    query = update.callback_query
    q = query.data
    if q == "cat_more":
        query.message.delete()
        user_agent = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                }

        search = "https://theoldreader.com/kittens/1366/768/js" #Запрашиваем у юзера, что он хочет найти
        url = requests.get(search, headers=user_agent) #Делаем запрос
        soup = BeautifulSoup(url.text, features="lxml") #Получаем запрос
        result = soup.find("img").get("src") #Ищем тег <img src="ссылка.png"
        result = "https://theoldreader.com" + result
        chat = update.effective_chat
        cat = [
                    [   
                        InlineKeyboardButton('Еще хочу котейку', callback_data='cat_more'),
                        InlineKeyboardButton('❌', callback_data='top_delete_message')
                    ]
                ]
        reply_markup = InlineKeyboardMarkup(cat)
        bot.send_photo(chat.id,photo=result, reply_markup=reply_markup, parse_mode= "Markdown")
    elif q == "cat_delete":
        query.message.delete()

BROADCAST_HANDLER = CommandHandler("cats", cats)
dispatcher.add_handler(BROADCAST_HANDLER)

top_callback_handler = CallbackQueryHandler(cat_button, pattern=r"cat_")
dispatcher.add_handler(top_callback_handler)