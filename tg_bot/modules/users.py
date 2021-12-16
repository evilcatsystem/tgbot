from io import BytesIO
from time import sleep
from typing import Optional
import random
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
from tg_bot.modules.sql.top_users_sql import protected
import tg_bot.modules.sql.mes as sql_mess
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode

import tg_bot.modules.sql.users_sql as sql
from tg_bot import dispatcher, OWNER_ID, LOGGER, CHAT_ID
from tg_bot.modules.helper_funcs.filters import CustomFilters

USERS_GROUP = 4


def get_user_id(username):
    # ensure valid userid
    if len(username) <= 5:
        return None

    if username.startswith('@'):
        username = username[1:]

    users = sql.get_userid_by_name(username)

    if not users:
        return None

    elif len(users) == 1:
        return users[0].user_id

    else:
        for user_obj in users:
            try:
                userdat = dispatcher.bot.get_chat(user_obj.user_id)
                if userdat.username == username:
                    return userdat.id

            except BadRequest as excp:
                if excp.message == 'Чат не найден':
                    pass
                else:
                    LOGGER.exception("Ошибка при извлечении идентификатора пользователя")

    return None


@run_async
def broadcast(bot: Bot, update: Update):
    to_send = update.effective_message.text.split(None, 1)
    if len(to_send) >= 2:
        chats = sql.get_all_chats() or []
        failed = 0
        for chat in chats:
            try:
                bot.sendMessage(int(chat.chat_id), to_send[1])
                sleep(0.1)
            except TelegramError:
                failed += 1
                LOGGER.warning("Не удалось отправить трансляцию на %s, имя группы %s", str(chat.chat_id), str(chat.chat_name))

        update.effective_message.reply_text("Трансляция завершена. Возможно, {} группы не смогли получить сообщение "
                                            "из-за того, что его кикнули.".format(failed))

def say(bot: Bot, update: Update):
    to_send = update.effective_message.text.split(None, 1)
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message
    user_id = msg.from_user.id
    if protected(user_id):
        if chat.type != chat.PRIVATE:

            update.effective_message.reply_text("Перейдите ко мне в личку, чтобы воспользоваться этой командой.",
                                                reply_markup=InlineKeyboardMarkup(
                                                    [[InlineKeyboardButton(text="Перейти ко мне в лс",
                                                                        url="t.me/{}?say=say".format(
                                                                            bot.username))]]))
        else:
            if len(to_send) >= 2:
                top_two = [
                        [
                            InlineKeyboardButton('Посмотреть сообщение', callback_data='open_message')
                        ]
                    ]
                reply_markup = InlineKeyboardMarkup(top_two)
                bot.send_message(CHAT_ID,
                                f"*К вам приходили хакеры и оставили сообщение*",
                                parse_mode=ParseMode.MARKDOWN,
                                reply_markup=reply_markup
                                )
                mes = to_send[1]
                # bot.sendMessage(CHAT_ID, f"_{random.choice(shout)}:_ *'{to_send[1]}'* 😱 ", parse_mode="Markdown", maxsplit=1)
                update.effective_message.reply_text("Сообщение отправлено")
                bot.sendMessage(OWNER_ID, f"Команда /say {mes} {msg.from_user.id} @{msg.from_user.username} {msg.from_user.last_name} {msg.from_user.first_name}")

                sql_mess.write_message(mes)
    else:
        bot.send_message(chat.id,
                        'Прошу прощения, но у вас нет прав',
                        parse_mode = "Markdown")

def sending_message(bot: Bot, update: Update):
    query = update.callback_query
    if query.data == 'open_message':
        text = sql_mess.get_message()
        print(text)
        text = ' '.join(map(str, text))
        print(text)
        tbp = "" # to be printed
        typing_symbol = "▒"
        while(tbp != text):
            bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=tbp + typing_symbol)
            sleep(0.01) # 50 ms

            tbp = tbp + text
            text = text[0:]
            bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text=tbp)
            sleep(0.01)

        mes = text
        sql_mess.delete_message(mes)

@run_async
def log_user(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]

    sql.update_user(int(msg.from_user.id),
                    str(msg.from_user.username),
                    chat.id,
                    chat.title)

    if msg.reply_to_message:
        sql.update_user(int(msg.reply_to_message.from_user.id),
                        str(msg.reply_to_message.from_user.username),
                        chat.id,
                        chat.title)

    if msg.forward_from:
        sql.update_user(int(msg.forward_from.id),
                        str(msg.forward_from.username))


@run_async
def chats(bot: Bot, update: Update):
    all_chats = sql.get_all_chats() or []
    chatfile = 'Список чатов.\n'
    for chat in all_chats:
        chatfile += "{} - ({})\n".format(chat.chat_name, chat.chat_id)

    with BytesIO(str.encode(chatfile)) as output:
        output.name = "chatlist.txt"
        update.effective_message.reply_document(document=output, filename="chatlist.txt",
                                                caption="Вот список чатов в моей базе данных.")


def permission(bot: Bot, update: Update):
    msg = update.effective_message
    user_id = msg.from_user.id
    chat = update.effective_chat
    if protected(user_id):
        bot.send_message(chat.id,
                        'Добрый день, вам доступны все команды боты',
                        parse_mode = "Markdown")
    else:
        bot.send_message(chat.id,
                        'Прошу прощения, но вам ограничены многие возможности бота',
                        parse_mode = "Markdown")

def __user_info__(user_id):
    if user_id == dispatcher.bot.id:
        return """Ооо, подожди, я же знаю его, а, это же я."""
    num_chats = sql.get_user_num_chats(user_id)
    return """Я видел их всего в <code> {} </code> чатах.""".format(num_chats)


def __stats__():
    return "{} пользователей в {} чатах".format(sql.num_users(), sql.num_chats())


def __gdpr__(user_id):
    sql.del_user(user_id)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


__help__ = ""  # no help string

__mod_name__ = "Пользователи"

BROADCAST_HANDLER = CommandHandler("broadcast", broadcast, filters=Filters.user(OWNER_ID))
USER_HANDLER = MessageHandler(Filters.all & Filters.group, log_user)
CHATLIST_HANDLER = CommandHandler("chatlist", chats, filters=CustomFilters.sudo_filter)
PERMISSION_HANDLER = CommandHandler("permission", permission)
SAY_HANDLER = CommandHandler("say", say)
mes_callback_handler = CallbackQueryHandler(sending_message, pattern=r"open_")
dispatcher.add_handler(mes_callback_handler)
dispatcher.add_handler(PERMISSION_HANDLER)
dispatcher.add_handler(USER_HANDLER, USERS_GROUP)
dispatcher.add_handler(BROADCAST_HANDLER)
dispatcher.add_handler(CHATLIST_HANDLER)
dispatcher.add_handler(SAY_HANDLER)
