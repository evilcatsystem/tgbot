import requests
from bs4 import BeautifulSoup as bs

from telegram import Update, Bot
from telegram.ext import CommandHandler

from tg_bot import dispatcher

def kernel(bot: Bot, update: Update):
    update.effective_message.delete()
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6)"
           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Saf"
           "ari/537.36"}

    res = requests.get("https://kernel.org", headers = HEADERS)
    html = bs(res.text, "lxml")   # Запрос и получаем html

    versions = html.select("td strong")[1:]
    names = html.select("td")         # Ищем теги
    dates = html.select("td:nth-of-type(3)")
    links = html.select("a[title='Download complete tarball']")

    names_list = []
    versions_list = []           # Списки, некоторые нам понадобятся в будущем
    sort_names_list = []
    sort_date_list = []
    sort_links_list = []

    for line in versions:
        versions_list.append(line.get_text())     # Получаем список с версиями ядра

    for line in names:
        names_list.append(line.get_text())         # Получаем смешанный список с названием и ссылями

    for line in names_list: 
        if ":" in line:
            sort_names_list.append(line)           # Убираем все ненужное, отделяем ссылки
    sort_names_list = sort_names_list[3:]

    for line in links:
        sort_links_list.append(line.get("href"))  # Получаем ссылки
    
    for line in dates:
        sort_date_list.append(line.get_text())     # Получаем даты, без всякой херни
    full_info = list(zip(sort_names_list, versions_list, sort_date_list, sort_links_list))
    ##############################################################

    R = full_info
    full_info = []
    full_info_2 = []

    for line in R:
        for line_2 in line:
            if line_2 == line[3]: pass
            elif len(line_2) == 10:
                full_info.append("[{}]({})\n".format(line_2, line[3]))   
            else:
                full_info.append("[{}]({})".format(line_2, line[3]))

    for line in full_info:
        if "[EOL]" in line:
            eol = line.replace(" ", "")
            eol = eol.replace("[EOL]", " | EOL |")
            full_info_2.append(eol)
        else:
            full_info_2.append(line)
    full_info_2 = "  ".join(full_info_2) #
    chat = update.effective_chat
    bot.send_message(chat.id, "*Версии ядер Linux:* \n\n" + full_info_2, parse_mode = "Markdown")


__help__ = "Узнать версии ядер Linux."

__mod_name__ = "Версии ядер"

BROADCAST_HANDLER = CommandHandler("kernel", kernel)
dispatcher.add_handler(BROADCAST_HANDLER)
