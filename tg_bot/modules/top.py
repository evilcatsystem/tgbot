from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram import Chat, Update, Bot
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.utils.helpers import escape_markdown
from tg_bot import dispatcher, OWNER_ID, CHAT_ID
from tg_bot.modules.helper_funcs.chat_status import is_user_admin
import tg_bot.modules.global_bans as check_ban
import tg_bot.modules.sql.top_users_sql as sql
from tg_bot.modules.helper_funcs.get_user_top import get_user_top

def sets(bot: Bot, update: Update):
    user = update.effective_user
    mes = update.effective_message
    chat = update.effective_chat
    if user.id == OWNER_ID:
        message = update.message.text[5:]
        if mes.reply_to_message:
            user = update.effective_message.reply_to_message.from_user
            user_id = user.id
            bot.send_message(chat.id, "Пользователю {}, изменено количество сообщений на {}".format(
                    escape_markdown(user.first_name),
                    message))
        else:
            user = update.effective_user
            user_id = user.id
            bot.send_message(chat.id, "Пользователю {}, изменено количество сообщений на {}".format(
                    escape_markdown(user.first_name),
                    message))
        sql.set_top(user_id, message)
        update.effective_message.delete()
    else:
        update.effective_message.delete()
        bot.send_message(chat.id, "{}, недостаточно прав для применения этой команды".format(
                    escape_markdown(user.first_name)))


def top(bot: Bot, update: Update):
    update.effective_message.delete()
    chat = update.effective_chat
    get_user = get_user_top()[0:10]
    users = '\n'.join(get_user)
    top_two = [
            [
                InlineKeyboardButton('🔙', callback_data='top_three'),
                InlineKeyboardButton('❌', callback_data='top_delete_message'),
                InlineKeyboardButton('🔜', callback_data='top_two')
            ]
        ]
    reply_markup = InlineKeyboardMarkup(top_two)
    bot.send_message(chat.id, 
                    f"*Топ пользователей чата* \n\n{users}", 
                    parse_mode=ParseMode.MARKDOWN, 
                    reply_markup=reply_markup
                    )

# all other menus
def top_menu(bot: Bot, update: Update):
    query = update.callback_query
    if query.data == 'top_two':
        get_user = get_user_top()[10:20]
        users = '\n'.join(get_user)
        tops = [
                [
                    InlineKeyboardButton('🔙', callback_data='top_one'),
                    InlineKeyboardButton('❌', callback_data='top_delete_message'),
                    InlineKeyboardButton('🔜', callback_data='top_three')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(tops)
        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text=f"*Топ пользователей чата* \n\n{users}",
                              parse_mode=ParseMode.MARKDOWN,
                              reply_markup=reply_markup
                            )
    elif query.data == 'top_three':
        try:
            get_user = get_user_top()[20:30]
            users = '\n'.join(get_user)
            tops = [
                        [
                            InlineKeyboardButton('🔙', callback_data='top_two'),
                            InlineKeyboardButton('❌', callback_data='top_delete_message'),
                            InlineKeyboardButton('🔜', callback_data='top_one')
                        ]
                    ]
            reply_markup = InlineKeyboardMarkup(tops)
            bot.edit_message_text(chat_id=query.message.chat_id,
                                message_id=query.message.message_id,
                                text=f"*Топ пользователей чата* \n\n{users}",
                                parse_mode=ParseMode.MARKDOWN,
                                reply_markup=reply_markup)
        except:
            top_two = [
                    [
                        InlineKeyboardButton('🔙', callback_data='top_two'),
                        InlineKeyboardButton('❌', callback_data='top_delete_message')
                    ]
                ]
            reply_markup = InlineKeyboardMarkup(top_two)
            bot.edit_message_text(chat_id=query.message.chat_id,
                                message_id=query.message.message_id,
                                text=f"*Топ пользователей чата*",
                                parse_mode=ParseMode.MARKDOWN,
                                reply_markup=reply_markup
                                )
        
    elif query.data == 'top_one':
        get_user = get_user_top()[0:10]
        users = '\n'.join(get_user)

        top_two = [
                [   InlineKeyboardButton('🔙', callback_data='top_three'),
                    InlineKeyboardButton('❌', callback_data='top_delete_message'),
                    InlineKeyboardButton('🔜', callback_data='top_two')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(top_two)
        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text=f"*Топ пользователей чата* \n\n{users}",
                              parse_mode=ParseMode.MARKDOWN,
                              reply_markup=reply_markup
                            )
    elif query.data == 'top_delete_message':
        query.message.delete()


def write(bot: Bot, update: Update):
    """ Изменение значение в таблице """
    chat = update.effective_chat  # type: Optional[Chat]
    if chat.type != "private":
        if chat.id == CHAT_ID:
            msg = update.effective_message
            name = msg.from_user.first_name
            user_id = str(msg.from_user.id)
            user = update.effective_user
            if user and not is_user_admin(chat, user.id):
                check_ban.check_and_ban(update, user.id)
            sql.write_top(user_id, name)

__help__ = """Топ пользователей чата
- /top - Показать список активных пользователей"""

__mod_name__ = "Топ"

BROADCAST_HANDLER = CommandHandler("top", top)
dispatcher.add_handler(BROADCAST_HANDLER)
BROADCAST_HANDLER = CommandHandler("set", sets)
dispatcher.add_handler(BROADCAST_HANDLER)
top_callback_handler = CallbackQueryHandler(top_menu, pattern=r"top_")
dispatcher.add_handler(top_callback_handler)
dispatcher.add_handler(MessageHandler(Filters.chat(CHAT_ID) & Filters.text, write))


