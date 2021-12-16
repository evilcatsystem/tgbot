from typing import Optional

from telegram import Message, Update, Bot, User
from telegram import MessageEntity
from telegram.ext import Filters, MessageHandler, run_async

from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler, DisableAbleRegexHandler
from tg_bot.modules.sql import afk_sql as sql
from tg_bot.modules.users import get_user_id
from tg_bot.modules.sql.top_users_sql import protected


AFK_GROUP = 7
AFK_REPLY_GROUP = 8


@run_async
def afk(bot: Bot, update: Update):
    user = update.effective_user  # type: Optional[User]
    user_id = user.id
    if protected(user_id):
        args = update.effective_message.text.split(None, 1)
        if len(args) >= 2:
            reason = args[1]
        else:
            reason = ""

        sql.set_afk(update.effective_user.id, reason)
        update.effective_message.reply_text("{} ушел по делам!".format(update.effective_user.first_name))


@run_async
def no_longer_afk(bot: Bot, update: Update):
    user = update.effective_user  # type: Optional[User]

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
        update.effective_message.reply_text("{} пришел!".format(update.effective_user.first_name))


@run_async
def reply_afk(bot: Bot, update: Update):
    message = update.effective_message  # type: Optional[Message]
    if message.reply_to_message:
        user = update.effective_message.reply_to_message.from_user
        user_id = user.id
        fst_name = user.first_name
    else:
        entities = message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION])

        if message.entities and entities:
            for ent in entities:
                if ent.type == MessageEntity.TEXT_MENTION:
                    user_id = ent.user.id
                    fst_name = ent.user.first_name

                elif ent.type == MessageEntity.MENTION:
                    user_id = get_user_id(message.text[ent.offset:ent.offset + ent.length])
                    if not user_id:
                        # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                        return
                    chat = bot.get_chat(user_id)
                    fst_name = chat.first_name

                else:
                    return

    if sql.is_afk(user_id):
        valid, reason = sql.check_afk_status(user_id)
        if valid:
            if not reason:
                res = "{} в данный момент не в сети! Попросил не беспокоить.".format(fst_name)
                chat = update.effective_chat
                bot.send_message(chat.id,res)
            else:
                res = "{} в данный момент не в сети по причине: {}\nПопросил не беспокоить.".format(fst_name, reason)
                chat = update.effective_chat
                bot.send_message(chat.id,res)


def __gdpr__(user_id):
    sql.rm_afk(user_id)


__help__ = """
 - /afk <причина>: отметьте себя как AFK.
 - brb <причина>: то же, что и команда afk, но не команда.

Если помечено как AFK, на любые упоминания будет ответ с сообщением о том, что вы недоступны и удаляет упоминание о вас!
"""

__mod_name__ = "АФК"

AFK_HANDLER = DisableAbleCommandHandler("afk", afk)
AFK_REGEX_HANDLER = DisableAbleRegexHandler("(?i)brb", afk, friendly="afk")
NO_AFK_HANDLER = MessageHandler(Filters.all & Filters.group, no_longer_afk)
AFK_REPLY_HANDLER = MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION) | Filters.reply,
                                   reply_afk)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)
