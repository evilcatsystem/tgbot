
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackQueryHandler
from tg_bot.modules.sql.top_users_sql import protected
from tg_bot import dispatcher

def book(bot: Bot, update: Update):
    user = update.effective_user  
    user_id = user.id
    if protected(user_id):
        update.effective_message.delete()
        chat = update.effective_chat
        boook = [
            [
                InlineKeyboardButton("Книги📚", callback_data="book_books"),
                InlineKeyboardButton("Словари брут📖", callback_data="book_slovar"),
                InlineKeyboardButton("Видеокурсы📹", callback_data="book_video")
            ],
            [
                InlineKeyboardButton("Вкусняшки😋", callback_data="book_vkus"),
                InlineKeyboardButton("Сервисы😧", callback_data="book_servise"),
                InlineKeyboardButton("Аудиокниги🔊", callback_data="book_audio")
            ],
            [
                InlineKeyboardButton('❌', callback_data='book_delete_message')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(boook)
        bot.send_message(chat.id, "*Какой пункт выберешь?*", reply_markup=reply_markup, parse_mode="Markdown")

def books(bot: Bot, update: Update):
    query = update.callback_query
    q = query.data
    
    if q == 'book_books':
        book = [
                [
                    InlineKeyboardButton("🔙", callback_data="book_menu"),
                    InlineKeyboardButton("❌", callback_data="book_delete_message"),
                    InlineKeyboardButton('🔜', url='https://dubox.com/s/1lwShaFYhsshA5seYbRzW1A')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(book)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*Книги, читаем и развиваемся*📚 \n пароль: 3ssh",
                                reply_markup=reply_markup, parse_mode="Markdown")
    elif q == 'book_slovar':
        slovar = [
                [
                    InlineKeyboardButton("🔙", callback_data="book_menu"),
                    InlineKeyboardButton("❌", callback_data="book_delete_message"),
                    InlineKeyboardButton('🔜', url='https://dubox.com/s/15vEzHpjpcx1JrFJChpyIiQ')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(slovar)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*Словари для брутфорса*📖 \nпароль: cc1q",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")

    elif q == 'book_video':
        video = [
                [
                    InlineKeyboardButton("🔙", callback_data="book_menu"),
                    InlineKeyboardButton("❌", callback_data="book_delete_message"),
                    InlineKeyboardButton('🔜', url='https://dubox.com/s/1TAx89ypbXMkXRbBuHOt_Rg')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(video)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*Видеокурсы*📹 \nпароль: 5g4g",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")

    elif q == 'book_vkus':
        vkus = [
                [
                    InlineKeyboardButton("🔙", callback_data="book_menu"),
                    InlineKeyboardButton("❌", callback_data="book_delete_message"),
                    InlineKeyboardButton('🔜', url='https://dubox.com/s/145Xg894LJZU7xa4Bx73DvA')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(vkus)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*Вкусняшки*😋 \nпароль: ycdr",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")
    elif q == 'book_servise':
        service = [
                [
                    InlineKeyboardButton("🔙", callback_data="book_menu"),
                    InlineKeyboardButton("❌", callback_data="book_delete_message"),
                    InlineKeyboardButton('🔜', url='https://dubox.com/s/14RpCvNzrvfaCGfmcdy26Yw')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(service)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*Сервисы*😧 \nпароль: 8d44",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")

    elif q == 'book_audio':
        audio = [
                [
                    InlineKeyboardButton("🔙", callback_data="book_menu"),
                    InlineKeyboardButton("❌", callback_data="book_delete_message"),
                    InlineKeyboardButton('🔜', url='https://dubox.com/s/1q9pcOdYJKFqIvRIP0jNacw')
                ]
            ]
        reply_markup = InlineKeyboardMarkup(audio)

        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*Аудиокурсы*🔊 \nпароль: 29sv",
                                reply_markup=reply_markup,
                                parse_mode="Markdown")
    
    elif q == 'book_menu':
        boook = [
            [
                InlineKeyboardButton("Книги📚", callback_data="book_books"),
                InlineKeyboardButton("Словари брут📖", callback_data="book_slovar"),
                InlineKeyboardButton("Видеокурсы📹", callback_data="book_video")
            ],
            [
                InlineKeyboardButton("Вкусняшки😋", callback_data="book_vkus"),
                InlineKeyboardButton("Сервисы😧", callback_data="book_servise"),
                InlineKeyboardButton("Аудиокниги🔊", callback_data="book_audio")
            ],
            [
                InlineKeyboardButton('❌', callback_data='book_delete_message')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(boook)
        bot.edit_message_text(chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              text="*Какой пункт выберешь?*", reply_markup=reply_markup,
                                parse_mode="Markdown")
    elif q == 'book_delete_message':
        query.message.delete()



__help__ = "/book - Читаем, учимся, познаем новое"

__mod_name__ = "Сборники книг"



BROADCAST_HANDLER = CommandHandler("book", book)
dispatcher.add_handler(BROADCAST_HANDLER)
book_callback_handler = CallbackQueryHandler(books, pattern=r"book_")
dispatcher.add_handler(book_callback_handler)