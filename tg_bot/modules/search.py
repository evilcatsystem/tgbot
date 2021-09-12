import wikipediaapi #pip install Wikipedia-API

import requests
from bs4 import BeautifulSoup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackQueryHandler

from tg_bot import dispatcher

def search(bot: Bot, update: Update):
    update.effective_message.delete()
    user_agent = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    search = update.message.text[8:] #Запрашиваем у юзера, что он хочет найти
    url = requests.get('https://www.google.com/search?q=' + search, headers=user_agent) #Делаем запрос
    soup = BeautifulSoup(url.text, features="lxml") #Получаем запрос
    r = soup.find_all("div", class_="yuRUbf") #Выводи весь тег div class="r"
    results_news = []
    for s in r:
        link = s.find('a').get('href') #Ищем ссылки по тегу <a href="example.com"
        title = s.find("h3", {'class': 'LC20lb DKV0Md'}) #Ищем описание ссылки по тегу <h3 class="LC20lb DKV0Md" 
        title = title.get_text() #Вытаскиваем описание
        results = f"[{title}]({link})"
        results_news.append(results)
        result = "\n".join(results_news)
    chat = update.effective_chat
    delete = [
            [
                InlineKeyboardButton('❌', callback_data='search_delete')
            ]
        ]
    reply_markup = InlineKeyboardMarkup(delete)
    bot.send_message(chat.id, 
                    f'Результаты по запросу: "{search}"\n\n{result}', 
                    parse_mode = "Markdown", 
                    disable_web_page_preview=True, 
                    reply_markup=reply_markup)

def wikipedia(bot: Bot, update: Update):
    try:
        wiki_wiki = wikipediaapi.Wikipedia(
            language='ru',
            extract_format=wikipediaapi.ExtractFormat.WIKI)
        page_py = wiki_wiki.page(update.message.text[6:])
        top_two = [
            [
                InlineKeyboardButton("Читать на Википедии", url=page_py.canonicalurl),
                InlineKeyboardButton('❌', callback_data='search_delete')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(top_two)
        chat = update.effective_chat
        bot.send_message(chat.id, 
                        page_py.summary, 
                        parse_mode = "Markdown", 
                        disable_web_page_preview=True, 
                        reply_markup=reply_markup)
        update.effective_message.delete()
    except:
        top_two = [
            [
                InlineKeyboardButton('❌', callback_data='search_delete')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(top_two)
        chat = update.effective_chat
        bot.send_message(chat.id, 
                        "По вашему запросу ничего не найдено", 
                        parse_mode = "Markdown", 
                        reply_markup=reply_markup)
        update.effective_message.delete()
        

def whois(bot: Bot, update: Update):
    update.effective_message.delete()
    try:
        HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6)"
           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Saf"
           "ari/537.36"}

        ip = str(update.message.text[6:])
        get = requests.get(f"https://ipinfo.io/{ip}/json", headers = HEADERS)
        get = get.json()
    
        list_first = []
        list_double = []

        for line in get:
            list_first.append(line)

        for line in get:
            list_double.append(get[line])
        full = []
        list_double = list(map(str, list_double))

        try:
            if "bogon" in list_first:
                full = ip + "\nЭто локальный ip"
            else:
                for line in list(zip(list_first, list_double)):
                    full.append(" ".join(line))
                
                if "status" in get: raise AttributeError

                full = "\n".join(full)
                id_ = full.find("readme")
        except Exception as e:
            full = f"*{ip}* - не корректен"

        chat = update.effective_chat
        delete = [
            [
                InlineKeyboardButton('❌', callback_data='search_delete')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(delete)
        bot.send_message(chat.id, 
                        "*" + full + "*", 
                        parse_mode = "Markdown", 
                        disable_web_page_preview=True, 
                        reply_markup=reply_markup)
    except Exception as e:
         print (f"❌❌❌❌❌ {e} ❌❌❌❌❌")

def search_delete(bot: Bot, update: Update):
    query = update.callback_query
    q = query.data
    if q == 'search_delete':
        query.message.delete()

__help__ = """/search <запрос> - поиск в google.com по вашему запросу
/wiki <запрос> - поиск на википедии по вашему запросу
/whois <ip> - поиск информации о ip адресе
"""

__mod_name__ = "Поиск"


SEARCH_HANDLER = CommandHandler("search", search)
dispatcher.add_handler(SEARCH_HANDLER)

WHOIS_HANDLER = CommandHandler("whois", whois)
dispatcher.add_handler(WHOIS_HANDLER)

WIKI_HANDLER = CommandHandler("wiki", wikipedia)
dispatcher.add_handler(WIKI_HANDLER)

search_callback_handler = CallbackQueryHandler(search_delete, pattern=r"search_")
dispatcher.add_handler(search_callback_handler)

