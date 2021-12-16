from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackQueryHandler
from tg_bot.modules.sql.top_users_sql import protected

from tg_bot import dispatcher

def linux_glav(bot: Bot, update: Update):
    user = update.effective_user 
    user_id = user.id
    if protected(user_id):
        update.effective_message.delete()
        chat = update.effective_chat
        linux_wiki = [
            [
                InlineKeyboardButton('Arch Linux', callback_data='linux_arch'),
                InlineKeyboardButton('Ubuntu Linux', callback_data='linux_ubuntu')
            ],
            [
                InlineKeyboardButton('Debian Linux', callback_data='linux_debian'),
                InlineKeyboardButton('Gentoo Linux', callback_data='linux_gentoo')
            ],
            [
                InlineKeyboardButton('LFS Linux', callback_data='linux_lfs'),
                InlineKeyboardButton('Kali Linux', callback_data='linux_kali')
            ],
            [
                InlineKeyboardButton('❌', callback_data='linux_delete_message')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(linux_wiki, row_width=2)
        bot.send_message(chat.id, "Привет братик пингвин, что желаешь?", reply_markup=reply_markup)

def linux_wiki(bot: Bot, update: Update):
    query = update.callback_query
    q = query.data
    
    if q == 'linux_arch':
        arch = [
                [
                    InlineKeyboardButton('Скачать', url='archlinux.org/download'),
                    InlineKeyboardButton('Вики', url='wiki.archlinux.org'),
                    InlineKeyboardButton('Gide install', url='https://clck.ru/N5eWx')
                ],
                [
                    InlineKeyboardButton('🔙', callback_data="linux_infa"),
                    InlineKeyboardButton('❌', callback_data='linux_delete_message')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(arch)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*[Arch Linux]  Для самых привер"
                                    "едливых*",
                                reply_markup=reply_markup, parse_mode="Markdown")
    elif q == 'linux_ubuntu':
        ubuntu = [
                [
                    InlineKeyboardButton('Скачать', url='releases.ubuntu.com'),
                    InlineKeyboardButton('Вики', url='help.ubuntu.ru/wiki/главная')
                ],
                [
                    InlineKeyboardButton('🔙', callback_data="linux_infa"),
                    InlineKeyboardButton('❌', callback_data='linux_delete_message')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(ubuntu)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*[Ubuntu Linux]   Для самых маленьких"
                                    "котят*",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")

    elif q == 'linux_debian':
        debian = [
                [
                    InlineKeyboardButton('Скачать', url='debian.org/CD/'),
                    InlineKeyboardButton('Вики', url='wiki.debian.org/ru/DebianRussian')
                ],
                [
                    InlineKeyboardButton('🔙', callback_data="linux_infa"),
                    InlineKeyboardButton('❌', callback_data='linux_delete_message')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(debian)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*[Debian Linux]   Для любителей "
                                    "серверов*",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")

    elif q == 'linux_gentoo':
        gentoo = [
                [
                    InlineKeyboardButton('Скачать', url='gentoo.org/downloads'),
                    InlineKeyboardButton('Handbook', url='wiki.gentoo.org/wiki/Handbook:Main_Pagecg/ru')
                ],
                [
                    InlineKeyboardButton('🔙', callback_data="linux_infa"),
                    InlineKeyboardButton('❌', callback_data='linux_delete_message')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(gentoo)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*[Gentoo Linux]   Для вегетарианцев*",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")
    elif q == 'linux_lfs':
        debian = [
                [
                    InlineKeyboardButton('Скачать', url='linuxfromscratch.org'),
                    InlineKeyboardButton('Russian book', url='book.linuxfromscratch.ru')
                ],
                [
                    InlineKeyboardButton('🔙', callback_data="linux_infa"),
                    InlineKeyboardButton('❌', callback_data='linux_delete_message')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(debian)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*[LFS Linux]  "
                                "Тут даже нечего сказать*",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")

    elif q == 'linux_kali':
        debian = [
                [
                    InlineKeyboardButton('Скачать', url='https://www.kali.org/get-kali/'),
                    InlineKeyboardButton('Взломать', url='https://clck.ru/JwL3')
                ],
                [
                    InlineKeyboardButton('🔙', callback_data="linux_infa"),
                    InlineKeyboardButton('❌', callback_data='linux_delete_message')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(debian)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*[Kall Linux]   Наше время пришло,"
                                " мой друг*",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")
    
    elif q == 'linux_infa':
        linux_wiki =  [
            [
                InlineKeyboardButton('Arch Linux', callback_data='linux_arch'),
                InlineKeyboardButton('Ubuntu Linux', callback_data='linux_ubuntu')
            ],
            [
                InlineKeyboardButton('Debian Linux', callback_data='linux_debian'),
                InlineKeyboardButton('Gentoo Linux', callback_data='linux_gentoo')
            ],
            [
                InlineKeyboardButton('LFS Linux', callback_data='linux_lfs'),
                InlineKeyboardButton('Kali Linux', callback_data='linux_kali')
            ],
            [
                InlineKeyboardButton('❌', callback_data='linux_delete_message')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(linux_wiki)
        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="Привет братик пингвин, что желаешь?", reply_markup=reply_markup)
    elif q == 'linux_delete_message':
        query.message.delete()


__help__ = "/linux Получить помощь по линуксу"

__mod_name__ = "wiki linux"



BROADCAST_HANDLER = CommandHandler("linux", linux_glav)
dispatcher.add_handler(BROADCAST_HANDLER)
linux_callback_handler = CallbackQueryHandler(linux_wiki, pattern=r"linux_")
dispatcher.add_handler(linux_callback_handler)
