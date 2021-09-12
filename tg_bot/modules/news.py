import requests
from bs4 import BeautifulSoup

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackQueryHandler

from tg_bot import dispatcher

def news(bot: Bot, update: Update):
    user_agent = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
                    }
    url = requests.get('https://www.opennet.ru/#', headers=user_agent)
    soup = BeautifulSoup(url.text, features="lxml")

    tags = soup.find_all('td', class_="tnews")
    results_news = []
    for b in tags:
        url = b.find('a').get('href')
        title = b.find('a').text
        results = f'<a href="https://www.opennet.ru{url}">{title}</a>'
        results_news.append(results)
        results_lists_news = "\n".join(results_news)
    chat = update.effective_chat
    delete = [
            [
                InlineKeyboardButton('❌', callback_data='news_delete')
            ]
        ]
    reply_markup = InlineKeyboardMarkup(delete)
    bot.send_message(chat.id, 
                    f"\n🆕 Новости 🆕\n{results_lists_news}", 
                    disable_web_page_preview=True, 
                    reply_markup=reply_markup, 
                    parse_mode="HTML")

def news_delete(bot: Bot, update: Update):
    query = update.callback_query
    q = query.data
    if q == "news_delete":
        query.message.delete()

BROADCAST_HANDLER = CommandHandler("news", news)
dispatcher.add_handler(BROADCAST_HANDLER)

search_callback_handler = CallbackQueryHandler(news_delete, pattern=r"news_")
dispatcher.add_handler(search_callback_handler)