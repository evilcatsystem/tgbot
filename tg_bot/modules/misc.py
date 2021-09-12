import html
import json
import random
from datetime import datetime
from typing import Optional, List

import requests
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html

from tg_bot import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, BAN_STICKER
from tg_bot.__main__ import GDPR
from tg_bot.__main__ import STATS, USER_INFO
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.helper_funcs.filters import CustomFilters

RUN_STRINGS = (
    "Как ты думаешь, ты собираешься?",
    "Хм? какие? они ушли?",
    "Не так быстро...",
    "Не оставляйте меня с ними наедине !!",
    "Вы бежите, вы умираете.",
    "Ты пожалеешь об этом ...",
    "Вы также можете попробовать /kickme, я слышал, это весело.",
    "Вы можете бежать, но не можете спрятаться.",
    "Это все, что у тебя есть?",
    "Я сзади...",
    "У тебя есть компания!",
    "Мы можем сделать это легким путем или трудным путем.",
    "Вы просто не понимаете, не так ли?",
    "Ага, тебе лучше бежать!",
    "Напомните, пожалуйста, как я забочусь?",
    "На твоем месте я бы бежал быстрее.",
    "Это определенно тот дроид, который нам нужен.",
    "Пусть шансы всегда будут в вашу пользу.",
    "Знаменитые последние слова.",
    "И они исчезли навсегда, и больше их никто не видел.",
    "\"Ой, посмотри на меня! Я такой классный, могу убежать от бота! \"- этот человек",
    "Yeah yeah, just tap /kickme already.",
    "Вот, возьми это кольцо и отправляйся в Мордор, пока будешь на нем.",
    "Легенда гласит, что они все еще работают ...",
    "В отличие от Гарри Поттера, твои родители не могут защитить тебя от меня.",
    "Страх ведет к гневу. Гнев ведет к ненависти. Ненависть ведет к страданиям. Если вы продолжаете бежать в страхе, вы можете"
    "После нескольких вычислений я решил, что мой интерес к вашим махинациям равен нулю.",
    "Легенда гласит, что они все еще работают.",
    "Так держать, в любом случае не уверен, что мы хотим, чтобы ты был здесь.",
    "Ты волшебник- Ой. Подожди. Ты не Гарри, продолжай двигаться.",
    "Hasta la vista, детка.",
    "Кто выпустил собак?",
    "Это забавно, потому что всем плевать.",
    "Честно говоря, моя дорогая, мне наплевать.",
    "Давным-давно, в далекой галактике ... Кого-то это могло бы волновать. Но сейчас нет.",
    "Эй, посмотри на них! Они бегут от неизбежного банхаммера ... Милый.",
    "Хан выстрелил первым. И я тоже.",
    "Как сказал бы Доктор ... БЕГИ!",
)

SLAP_TEMPLATES = (
    "{user1} {throws} {item} в {user2}.",
)

ITEMS = (
    "чугунной сковородой",
    "большой форелью",
    "бейсбольной битой",
    "битой для крикета",
    "деревянной тростью",
    "принтером",
    "лопатой",
    "монитором",
    "учебником физики",
    "тостером",
    "портретом Ричарда Столмена",
    "телевизором",
    "рулоном изоленты",
    "книгой",
    "ноутбуком",
    "старым телевизором",
    "мешком камней",
    "камнем",
    "кружкой",
    "селедкой",
    "стулом",
    "подушкой",
)

THROW = (
    "бросает",
    "швыряет",
    "кидает",

)

HIT = (
    "ударяет",
    "дает пощечину",
)




GMAPS_LOC = "https://maps.googleapis.com/maps/api/geocode/json"
GMAPS_TIME = "https://maps.googleapis.com/maps/api/timezone/json"


@run_async
def runs(bot: Bot, update: Update):
    update.effective_message.reply_text(random.choice(RUN_STRINGS))


@run_async
def slap(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_text = msg.reply_to_message.reply_text if msg.reply_to_message else msg.reply_text

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(msg.from_user.first_name, msg.from_user.id)

    user_id = extract_user(update.effective_message, args)
    if user_id:
        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        if slapped_user.username:
            user2 = "@" + escape_markdown(slapped_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(slapped_user.first_name,
                                                   slapped_user.id)

    # if no target found, bot targets the sender
    else:
        user1 = "[{}](tg://user?id={})".format(bot.first_name, bot.id)
        user2 = curr_user

    temp = random.choice(SLAP_TEMPLATES)
    item = random.choice(ITEMS)
    hit = random.choice(HIT)
    throw = random.choice(THROW)

    repl = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(repl, parse_mode=ParseMode.MARKDOWN)


@run_async
def get_bot_ip(bot: Bot, update: Update):
    """ Отправляет IP-адрес бота, чтобы иметь возможность подключиться по ssh в случае необходимости.
        ТОЛЬКО ВЛАДЕЛЬЦА.
    """
    res = requests.get("http://ipinfo.io/ip")
    update.message.reply_text(res.text)


@run_async
def get_id(bot: Bot, update: Update, args: List[str]):
    user_id = extract_user(update.effective_message, args)
    if user_id:
        if update.effective_message.reply_to_message and update.effective_message.reply_to_message.forward_from:
            user1 = update.effective_message.reply_to_message.from_user
            user2 = update.effective_message.reply_to_message.forward_from
            update.effective_message.reply_text(
                "отправитель, {}, имеет идентификатор `{}`. \nПересылка, {}, имеет идентификатор`{}`.".format(
                    escape_markdown(user2.first_name),
                    user2.id,
                    escape_markdown(user1.first_name),
                    user1.id),
                parse_mode=ParseMode.MARKDOWN)
        else:
            user = bot.get_chat(user_id)
            update.effective_message.reply_text("{} айди `{}`.".format(escape_markdown(user.first_name), user.id),
                                                parse_mode=ParseMode.MARKDOWN)
    else:
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == "private":
            update.effective_message.reply_text("Твое айди `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)

        else:
            update.effective_message.reply_text("Айди чата `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)


@run_async
def info(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message  # type: Optional[Message]
    user_id = extract_user(update.effective_message, args)

    if user_id:
        user = bot.get_chat(user_id)

    elif not msg.reply_to_message and not args:
        user = msg.from_user

    elif not msg.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not msg.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        msg.reply_text("Я не могу извлечь из этого сообщения пользователя.")
        return

    else:
        return

    text = "<b>Информация о пользователе</b>:" \
           "\nID: <code>{}</code>" \
           "\nИмя: {}".format(user.id, html.escape(user.first_name))

    if user.last_name:
        text += "\nФамилия: {}".format(html.escape(user.last_name))

    if user.username:
        text += "\nЮзернейм: @{}".format(html.escape(user.username))

    text += "\nСсылка на пользователя: {}".format(mention_html(user.id, "link"))

    if user.id == OWNER_ID:
        text += "\n\nЭтот человек мой хозяин - я бы никогда ничего против него не сделал!"
    else:
        if user.id in SUDO_USERS:
            text += "\nЭтот человек - один из моих пользователей sudo! "\
                    "Почти такой же мощный, как мой владелец - так что следите за ним."
        else:
            if user.id in SUPPORT_USERS:
                text += "\nЭтот человек - один из моих пользователей службы поддержки! "\
                        "Не совсем пользователь sudo, но все же может заблокировать вас с карты"

            if user.id in WHITELIST_USERS:
                text += "\nЭтот человек внесен в белый список! "\
                        "Это означает, что мне не разрешено банить/выгнать его"

    for mod in USER_INFO:
        mod_info = mod.__user_info__(user.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


@run_async
def get_time(bot: Bot, update: Update, args: List[str]):
    location = " ".join(args)
    if location.lower() == bot.first_name.lower():
        update.effective_message.reply_text("Для меня это всегда банхаммер!")
        bot.send_sticker(update.effective_chat.id, BAN_STICKER)
        return

    res = requests.get(GMAPS_LOC, params=dict(address=location))

    if res.status_code == 200:
        loc = json.loads(res.text)
        if loc.get('status') == 'OK':
            lat = loc['results'][0]['geometry']['location']['lat']
            long = loc['results'][0]['geometry']['location']['lng']

            country = None
            city = None

            address_parts = loc['results'][0]['address_components']
            for part in address_parts:
                if 'country' in part['types']:
                    country = part.get('long_name')
                if 'administrative_area_level_1' in part['types'] and not city:
                    city = part.get('long_name')
                if 'locality' in part['types']:
                    city = part.get('long_name')

            if city and country:
                location = "{}, {}".format(city, country)
            elif country:
                location = country

            timenow = int(datetime.utcnow().timestamp())
            res = requests.get(GMAPS_TIME, params=dict(location="{},{}".format(lat, long), timestamp=timenow))
            if res.status_code == 200:
                offset = json.loads(res.text)['dstOffset']
                timestamp = json.loads(res.text)['rawOffset']
                time_there = datetime.fromtimestamp(timenow + timestamp + offset).strftime("%H:%M:%S on %A %d %B")
                update.message.reply_text("Это {} в {}".format(time_there, location))


@run_async
def echo(bot: Bot, update: Update):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message
    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)
    message.delete()


@run_async
def gdpr(bot: Bot, update: Update):
    update.effective_message.reply_text("Удаление индентификаторов...")
    for mod in GDPR:
        mod.__gdpr__(update.effective_user.id)

    update.effective_message.reply_text("Ваши персональные данные были удалены",
                                        parse_mode=ParseMode.MARKDOWN)


MARKDOWN_HELP = """
Markdown - очень мощный инструмент форматирования, поддерживаемый Telegram. {} имеет некоторые улучшения, чтобы убедиться, что \
сохраненные сообщения правильно анализируются и позволяют создавать кнопки.

- <code>_italic_</code>: если обернуть текст символом '_', текст будет выделен курсивом
- <code>*bold*</code>: если обернуть текст символом '*', текст будет выделен жирным шрифтом.
- <code>`code`</code>: обтекание текста символом '' приведет к появлению моноширинного текста, пример 'код'
- <code>[sometext](someURL)</code>: это создаст ссылку - сообщение просто покажет <code>sometext</code>, \
и нажатие на ссылку откроет страницу по адресу <code>someURL</code>.
Образец: <code>[test](example.com)</code>

- <code>[buttontext](buttonurl:someURL)</code>: это специальное улучшение, позволяющее пользователям получать телеграм\
кнопки в markdown. <code>buttontext</code> будет то, что отображается на кнопке, и <code>someurl</code> \
будет URL-адрес, который открывается.
Образец: <code>[This is a button](buttonurl:example.com)</code>

Если вы хотите, чтобы в одной строке было несколько кнопок, используйте :same, как таковое:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
Это создаст две кнопки в одной строке вместо одной кнопки в строке.

Помните, что ваше сообщение <b> ДОЛЖНО </b> содержать какой-либо текст, кроме кнопки!
""".format(dispatcher.bot.first_name)


@run_async
def markdown_help(bot: Bot, update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text("Попробуйте переслать мне следующее сообщение, и вы увидите!")
    update.effective_message.reply_text("/save test Это тест на оценку. _italics_, *bold*, `code`, "
                                        "[URL](example.com) [button](buttonurl:github.com) "
                                        "[button2](buttonurl://google.com:same)")


@run_async
def stats(bot: Bot, update: Update):
    update.effective_message.reply_text("Текущая статистика:\n" + "\n".join([mod.__stats__() for mod in STATS]))

def ping(bot: Bot, update: Update):
    update.effective_message.reply_text("Pong!")


# /ip is for private use
__help__ = """
 - /id: получить текущий идентификатор группы. Если используется для ответа на сообщение, получает идентификатор этого пользователя.
 - /runs: ответить случайной строкой из массива ответов.
 - /slap: дать пощечину пользователю или получить пощечину, если не ответит.
 - /info: получить информацию о пользователе.
 - /gdpr: удаляет вашу информацию из базы данных бота. Только приватные чаты.

 - /markdownhelp: краткое описание того, как работает markdown в Telegram - можно вызвать только в приватных чатах.
"""

__mod_name__ = "Разное"

ID_HANDLER = DisableAbleCommandHandler("id", get_id, pass_args=True)
IP_HANDLER = CommandHandler("ip", get_bot_ip, filters=Filters.chat(OWNER_ID))

TIME_HANDLER = CommandHandler("time", get_time, pass_args=True)

RUNS_HANDLER = DisableAbleCommandHandler("runs", runs)
SLAP_HANDLER = DisableAbleCommandHandler("slap", slap, pass_args=True)
INFO_HANDLER = DisableAbleCommandHandler("info", info, pass_args=True)

ECHO_HANDLER = CommandHandler("echo", echo, filters=Filters.user(OWNER_ID))
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, filters=Filters.private)

STATS_HANDLER = CommandHandler("stats", stats, filters=CustomFilters.sudo_filter)
GDPR_HANDLER = CommandHandler("gdpr", gdpr, filters=Filters.private)

PING_HANDLER = CommandHandler("ping", ping)

dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(IP_HANDLER)
dispatcher.add_handler(TIME_HANDLER)
dispatcher.add_handler(RUNS_HANDLER)
dispatcher.add_handler(SLAP_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(STATS_HANDLER)
dispatcher.add_handler(GDPR_HANDLER)
dispatcher.add_handler(PING_HANDLER)
