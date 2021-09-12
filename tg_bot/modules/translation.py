
from telegram import Update, Bot
from telegram.ext import CommandHandler
from yandexfreetranslate import YandexFreeTranslate

from tg_bot import dispatcher


def translate(bot: Bot, update: Update):
    yt = YandexFreeTranslate()
    if update.message.text[3:5] == "ru":
        if update.effective_message.reply_to_message:
            msg = update.effective_message.reply_to_message
            trans = yt.translate("en", "ru", msg.text)
        else:
            translate = update.message.text[6:] 
            trans = yt.translate("en", "ru", translate)
    elif update.message.text[3:5] == "en":
        if update.effective_message.reply_to_message:
            msg = update.effective_message.reply_to_message
            trans = yt.translate("ru", "en", msg.text)
        else:
            translate = update.message.text[6:] 
            trans = yt.translate("ru", "en", translate)
    try:
        update.effective_message.reply_text(trans)
    except:
        update.effective_message.reply_text("Произошел троллинг")


__help__ = """
 - /t ru: Перевод текста с английского на русский
 - /t en: Перевод текста с русского на английский
"""

__mod_name__ = "Переводчик"


TRANSLATE_HANDLER = CommandHandler('t', translate)


dispatcher.add_handler(TRANSLATE_HANDLER)

