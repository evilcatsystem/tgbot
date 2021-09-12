from functools import wraps
from typing import Optional

from tg_bot.modules.helper_funcs.misc import is_module_loaded

FILENAME = __name__.rsplit(".", 1)[-1]

if is_module_loaded(FILENAME):
    from telegram import Bot, Update, ParseMode, Message, Chat
    from telegram.error import BadRequest, Unauthorized
    from telegram.ext import CommandHandler, run_async
    from telegram.utils.helpers import escape_markdown

    from tg_bot import dispatcher, LOGGER
    from tg_bot.modules.helper_funcs.chat_status import user_admin
    from tg_bot.modules.sql import log_channel_sql as sql


    def loggable(func):
        @wraps(func)
        def log_action(bot: Bot, update: Update, *args, **kwargs):
            result = func(bot, update, *args, **kwargs)
            chat = update.effective_chat  # type: Optional[Chat]
            message = update.effective_message  # type: Optional[Message]
            if result:
                if chat.type == chat.SUPERGROUP and chat.username:
                    result += "\n<b>Link:</b> " \
                              "<a href=\"http://telegram.me/{}/{}\">click here</a>".format(chat.username,
                                                                                           message.message_id)
                log_chat = sql.get_chat_log_channel(chat.id)
                if log_chat:
                    send_log(bot, log_chat, chat.id, result)
            elif result == "":
                pass
            else:
                LOGGER.warning("%s был установлен как регистрируемый, но не имел инструкции возврата.", func)

            return result

        return log_action


    def send_log(bot: Bot, log_chat_id: str, orig_chat_id: str, result: str):
        try:
            bot.send_message(log_chat_id, result, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            if excp.message == "Chat not found":
                bot.send_message(orig_chat_id, "Этот канал журнала был удален - не настроен.")
                sql.stop_chat_logging(orig_chat_id)
            else:
                LOGGER.warning(excp.message)
                LOGGER.warning(result)
                LOGGER.exception("Не удалось разобрать")

                bot.send_message(log_chat_id, result + "\n\nФорматирование было отключено из-за непредвиденной ошибки.")


    @run_async
    @user_admin
    def logging(bot: Bot, update: Update):
        message = update.effective_message  # type: Optional[Message]
        chat = update.effective_chat  # type: Optional[Chat]

        log_channel = sql.get_chat_log_channel(chat.id)
        if log_channel:
            log_channel_info = bot.get_chat(log_channel)
            message.reply_text(
                "Все журналы этой группы отправлены на: {} (`{}`)".format(escape_markdown(log_channel_info.title),
                                                                         log_channel),
                parse_mode=ParseMode.MARKDOWN)

        else:
            message.reply_text("Для этой группы не задан канал журнала.!")


    @run_async
    @user_admin
    def setlog(bot: Bot, update: Update):
        message = update.effective_message  # type: Optional[Message]
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == chat.CHANNEL:
            message.reply_text("Теперь перенаправьте /setlog группе, к которой вы хотите привязать этот канал.!")

        elif message.forward_from_chat:
            sql.set_chat_log_channel(chat.id, message.forward_from_chat.id)
            try:
                message.delete()
            except BadRequest as excp:
                if excp.message == "Message to delete not found":
                    pass
                else:
                    LOGGER.exception("Ошибка при удалении сообщения в канале журнала. Все равно должно сработать.")

            try:
                bot.send_message(message.forward_from_chat.id,
                                 "Этот канал был установлен как канал журнала для{}.".format(
                                     chat.title or chat.first_name))
            except Unauthorized as excp:
                if excp.message == "Запрещено: бот не является участником чата канала":
                    bot.send_message(chat.id, "Канал журнала настроен успешно!")
                else:
                    LOGGER.exception("ОШИБКА в настройке канала журнала.")

            bot.send_message(chat.id, "Канал журнала настроен успешно!")

        else:
            message.reply_text("Чтобы настроить канал журнала, выполните следующие действия: \n "
                               "- добавить бота на нужный канал \n"
                               "- отправить /setlog журнал на канал\n"
                               "- перенаправить /setlog группе\n")


    @run_async
    @user_admin
    def unsetlog(bot: Bot, update: Update):
        message = update.effective_message  # type: Optional[Message]
        chat = update.effective_chat  # type: Optional[Chat]

        log_channel = sql.stop_chat_logging(chat.id)
        if log_channel:
            bot.send_message(log_channel, "Канал отключен от {}".format(chat.title))
            message.reply_text("Канал журнала отключен.")

        else:
            message.reply_text("Канал журнала еще не установлен!")


    def __stats__():
        return "{} набор каналов журнала.".format(sql.num_logchannels())


    def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)


    def __chat_settings__(chat_id, user_id):
        log_channel = sql.get_chat_log_channel(chat_id)
        if log_channel:
            log_channel_info = dispatcher.bot.get_chat(log_channel)
            return "Все журналы этой группы отправлены на:{} (`{}`)".format(escape_markdown(log_channel_info.title),
                                                                            log_channel)
        return "Для этой группы не установлен канал журнала! "


    __help__ = """
*Только админам:*
- /logchannel: получить лог чата
- /setlog: установить логирование чата.
- /unsetlog: отключить логирование чата.

Настройка канала журнала выполняется:
- добавление бота на нужный канал (как админ!))
- отправка /setlog в чат
- пересылка /setlog в группу
"""

    __mod_name__ = "Лог чата"

    LOG_HANDLER = CommandHandler("logchannel", logging)
    SET_LOG_HANDLER = CommandHandler("setlog", setlog)
    UNSET_LOG_HANDLER = CommandHandler("unsetlog", unsetlog)

    dispatcher.add_handler(LOG_HANDLER)
    dispatcher.add_handler(SET_LOG_HANDLER)
    dispatcher.add_handler(UNSET_LOG_HANDLER)

else:
    # run anyway if module not loaded
    def loggable(func):
        return func
