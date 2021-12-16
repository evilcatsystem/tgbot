import html
from typing import Optional, List


from telegram import Message, Chat, Update, Bot, User
from telegram import ParseMode, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler, run_async
from telegram.utils.helpers import mention_markdown, mention_html, escape_markdown

import tg_bot.modules.sql.welcome_sql as sql
import tg_bot.modules.sql.top_users_sql as sql_top
import tg_bot.modules.sql.global_bans_sql as sql_ban
from tg_bot import dispatcher, OWNER_ID, LOGGER, CHAT_ID
from tg_bot.modules.helper_funcs.chat_status import user_admin, bot_can_delete
from tg_bot.modules.helper_funcs.misc import build_keyboard, revert_buttons
from tg_bot.modules.helper_funcs.msg_types import get_welcome_type
from tg_bot.modules.helper_funcs.string_handling import markdown_parser, \
    escape_invalid_curly_brackets
from tg_bot.modules.log_channel import loggable

VALID_WELCOME_FORMATTERS = ['first', 'last', 'fullname', 'username', 'id', 'count', 'chatname', 'mention']

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video
}

# do not async
def send(update, message, keyboard, backup_message):
    try:
        msg = update.effective_message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    except IndexError:
        msg = update.effective_message.reply_text(markdown_parser(backup_message + "\nПримечание: текущее сообщение было "
                                                                  "недействительно из-за проблем. Может быть"
                                                                  "из-за имени пользователя."),
                                                  parse_mode=ParseMode.MARKDOWN)
    except KeyError:
        msg = update.effective_message.reply_text(markdown_parser(backup_message + "\nПримечание: текущее сообщение: "
                                                                  "недействительно из-за проблемы с некоторыми неуместными"
                                                                  "фигурными скобками. Обновите"),
                                                  parse_mode=ParseMode.MARKDOWN)
    except BadRequest as excp:
        if excp.message == "Button_url_invalid":
            msg = update.effective_message.reply_text(markdown_parser(backup_message + "\nПримечание: у текущего сообщения недействительный URL "
                                                                      "на одной из кнопок. Обновите."),
                                                      parse_mode=ParseMode.MARKDOWN)
        elif excp.message == "Unsupported url protocol":
            msg = update.effective_message.reply_text(markdown_parser(backup_message + "\nПримечание: в текущем сообщении есть кнопки, которые "
                                                                      "используют протоколы URL, которые не поддерживаются"
                                                                      "Телеграммом. Пожалуйста, обновите."),
                                                      parse_mode=ParseMode.MARKDOWN)
        elif excp.message == "Wrong url host":
            msg = update.effective_message.reply_text(markdown_parser(backup_message + "\nПримечание: в текущем сообщении есть неправильные URL-адреса. "
                                                                      "Пожалуйста обновите."),
                                                      parse_mode=ParseMode.MARKDOWN)
            LOGGER.warning(message)
            LOGGER.warning(keyboard)
            LOGGER.exception("Не удалось разобрать! получил неверный URL-адрес хоста")
        else:
            msg = update.effective_message.reply_text(markdown_parser(backup_message + "\nПримечание. Произошла ошибка при отправке "
                                                                      "персонализированного сообщения. Пожалуйста, обновите."),
                                                      parse_mode=ParseMode.MARKDOWN)
            LOGGER.exception()

    return msg


@run_async
@bot_can_delete
def new_member(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    should_welc, cust_welcome, welc_type = sql.get_welc_pref(chat.id)
    if should_welc:
        sent = None
        new_members = update.effective_message.new_chat_members
        for new_mem in new_members:
            # Give the owner a special welcome
            user_id = new_mem.id
            name = new_mem.first_name
            if sql_ban.is_user_gbanned(user_id):
                update.effective_chat.kick_member(user_id)
                update.effective_message.reply_text(f"@{new_mem.username} Это плохой человек, их здесь не должно быть!")
            else:
                if name == None:
                    name = new_mem.last_name
                try:
                    if chat.id == CHAT_ID:
                        sql_top.get_user_top(user_id, name)
                except:
                    pass
                if new_mem.id == OWNER_ID:
                    update.effective_message.reply_text("Создатель в доме, давай начнем эту вечеринку!")
                    continue

                # Don't welcome yourself
                elif new_mem.id == bot.id:
                    continue

                else:
                    # If welcome message is media, send with appropriate function
                    if welc_type != sql.Types.TEXT and welc_type != sql.Types.BUTTON_TEXT:
                        ENUM_FUNC_MAP[welc_type](chat.id, cust_welcome)
                        return
                    # else, move on
                    first_name = new_mem.first_name or "PersonWithNoName"  # edge case of empty name - occurs for some bugs.

                    if cust_welcome:
                        if new_mem.last_name:
                            fullname = "{} {}".format(first_name, new_mem.last_name)
                        else:
                            fullname = first_name
                        count = chat.get_members_count()
                        mention = mention_markdown(new_mem.id, first_name)
                        if new_mem.username:
                            username = "@" + escape_markdown(new_mem.username)
                        else:
                            username = mention

                        valid_format = escape_invalid_curly_brackets(cust_welcome, VALID_WELCOME_FORMATTERS)
                        res = valid_format.format(first=escape_markdown(first_name),
                                                last=escape_markdown(new_mem.last_name or first_name),
                                                fullname=escape_markdown(fullname), username=username, mention=mention,
                                                count=count, chatname=escape_markdown(chat.title), id=new_mem.id)
                        buttons = sql.get_welc_buttons(chat.id)
                        keyb = build_keyboard(buttons)
                    else:
                        res = sql.DEFAULT_WELCOME.format(first=first_name)
                        keyb = []

                    keyboard = InlineKeyboardMarkup(keyb)
                    sent = send(update, res, keyboard,
                                sql.DEFAULT_WELCOME.format(fullname=fullname, chatname=chat.title))  # type: Optional[Message]

        prev_welc = sql.get_clean_pref(chat.id)
        if prev_welc:
            try:
                bot.delete_message(chat.id, prev_welc)
            except BadRequest as excp:
                pass

            if sent:
                sql.set_clean_welcome(chat.id, sent.message_id)


@run_async
def left_member(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    
    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)
    if should_goodbye:
        left_mem = update.effective_message.left_chat_member
        user_id = left_mem.id
        try:
            sql_top.delete_user_top(user_id)
        except:
            pass
        if left_mem:
            # Ignore bot being kicked
            if left_mem.id == bot.id:
                return

            # Give the owner a special goodbye
            if left_mem.id == OWNER_ID:
                update.effective_message.reply_text("RIP юзер")
                return

            # if media goodbye, use appropriate function for it
            if goodbye_type != sql.Types.TEXT and goodbye_type != sql.Types.BUTTON_TEXT:
                ENUM_FUNC_MAP[goodbye_type](chat.id, cust_goodbye)
                return

            first_name = left_mem.first_name or "PersonWithNoName"  # edge case of empty name - occurs for some bugs.
            if cust_goodbye:
                if left_mem.last_name:
                    fullname = "{} {}".format(first_name, left_mem.last_name)
                else:
                    fullname = first_name
                count = chat.get_members_count()
                mention = mention_markdown(left_mem.id, first_name)
                if left_mem.username:
                    username = "@" + escape_markdown(left_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(cust_goodbye, VALID_WELCOME_FORMATTERS)
                res = valid_format.format(first=escape_markdown(first_name),
                                          last=escape_markdown(left_mem.last_name or first_name),
                                          fullname=escape_markdown(fullname), username=username, mention=mention,
                                          count=count, chatname=escape_markdown(chat.title), id=left_mem.id)
                buttons = sql.get_gdbye_buttons(chat.id)
                keyb = build_keyboard(buttons)

            else:
                res = sql.DEFAULT_GOODBYE
                keyb = []
            keyboard = InlineKeyboardMarkup(keyb)
            send(update, res, keyboard, sql.DEFAULT_GOODBYE)


@run_async
@user_admin
def welcome(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat  # type: Optional[Chat]
    # if no args, show current replies.
    if len(args) == 0 or args[0].lower() == "noformat":
        noformat = args and args[0].lower() == "noformat"
        pref, welcome_m, welcome_type = sql.get_welc_pref(chat.id)
        update.effective_message.reply_text(
            "В этом чате параметр приветствия установлен на: `{}`. \n*Приветственное сообщение "
            "(не заполняя {{}}):*".format(pref),
            parse_mode=ParseMode.MARKDOWN)

        if welcome_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)

        else:
            if noformat:
                ENUM_FUNC_MAP[welcome_type](chat.id, welcome_m)

            else:
                ENUM_FUNC_MAP[welcome_type](chat.id, welcome_m, parse_mode=ParseMode.MARKDOWN)

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_welc_preference(str(chat.id), True)
            update.effective_message.reply_text("Буду вежливым!")

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id), False)
            update.effective_message.reply_text("Я дуюсь, больше не здороваюсь.")

        else:
            # idek what you're writing, say yes or no
            update.effective_message.reply_text("Я понимаю только 'on/yes' или 'off/no'!")


@run_async
@user_admin
def goodbye(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat  # type: Optional[Chat]

    if len(args) == 0 or args[0] == "noformat":
        noformat = args and args[0] == "noformat"
        pref, goodbye_m, goodbye_type = sql.get_gdbye_pref(chat.id)
        update.effective_message.reply_text(
            "В этом чате параметр прощания установлен на: `{}`. \n*Прощальное сообщение "
            "(не заполняя {{}}):*".format(pref),
            parse_mode=ParseMode.MARKDOWN)

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, goodbye_m, keyboard, sql.DEFAULT_GOODBYE)

        else:
            if noformat:
                ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

            else:
                ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN)

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id), True)
            update.effective_message.reply_text("Мне будет жаль, когда люди уйдут!")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id), False)
            update.effective_message.reply_text("Они уходят, они мертвы для меня.")

        else:
            # idek what you're writing, say yes or no
            update.effective_message.reply_text("Я понимаю только 'on/yes' или 'off/no'!")


@run_async
@user_admin
@loggable
def set_welcome(bot: Bot, update: Update) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("Вы не указали, чем отвечать!")
        return ""

    sql.set_custom_welcome(chat.id, content or text, data_type, buttons)
    msg.reply_text("Пользовательское приветственное сообщение успешно настроено!")

    return "<b>{}:</b>" \
           "\n#SET_WELCOME" \
           "\n<b>Admin:</b> {}" \
           "\nУстановите приветственное сообщение.".format(html.escape(chat.title),
                                               mention_html(user.id, user.first_name))


@run_async
@user_admin
@loggable
def reset_welcome(bot: Bot, update: Update) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    sql.set_custom_welcome(chat.id, sql.DEFAULT_WELCOME, sql.Types.TEXT)
    update.effective_message.reply_text("Успешно сброшено приветственное сообщение по умолчанию!")
    return "<b>{}:</b>" \
           "\n#RESET_WELCOME" \
           "\n<b>Admin:</b> {}" \
           "\nВосстановить приветственное сообщение по умолчанию.".format(html.escape(chat.title),
                                                            mention_html(user.id, user.first_name))


@run_async
@user_admin
@loggable
def set_goodbye(bot: Bot, update: Update) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("Вы не указали, что ответить остроумием!")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
    msg.reply_text("Пользовательское прощальное сообщение успешно настроено!")
    return "<b>{}:</b>" \
           "\n#SET_GOODBYE" \
           "\n<b>Admin:</b> {}" \
           "\nУстановить прощальное сообщениe.".format(html.escape(chat.title),
                                               mention_html(user.id, user.first_name))


@run_async
@user_admin
@loggable
def reset_goodbye(bot: Bot, update: Update) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, sql.Types.TEXT)
    update.effective_message.reply_text("Успешно сбросить прощальное сообщение по умолчанию!")
    return "<b>{}:</b>" \
           "\n#RESET_GOODBYE" \
           "\n<b>Admin:</b> {}" \
           "\nСбросить прощальное сообщение.".format(html.escape(chat.title),
                                                 mention_html(user.id, user.first_name))


@run_async
@user_admin
@loggable
def clean_welcome(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
            update.effective_message.reply_text("Я должен удалить приветственные сообщения два дня назад")
        else:
            update.effective_message.reply_text("В настоящее время я не удаляю старые приветственные сообщения!")
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id), True)
        update.effective_message.reply_text("Я попробую удалить старые приветственные сообщения!")
        return "<b>{}:</b>" \
               "\n#CLEAN_WELCOME" \
               "\n<b>Admin:</b> {}" \
               "\nПереключил чистые приветствия на <code>ON</code>.".format(html.escape(chat.title),
                                                                         mention_html(user.id, user.first_name))
    elif args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id), False)
        update.effective_message.reply_text("I won't delete old welcome messages.")
        return "<b>{}:</b>" \
               "\n#CLEAN_WELCOME" \
               "\n<b>Admin:</b> {}" \
               "\nПереключил чистые приветствия на to <code>OFF</code>.".format(html.escape(chat.title),
                                                                          mention_html(user.id, user.first_name))
    else:
        # idek what you're writing, say yes or no
        update.effective_message.reply_text("Я понимаю только 'on/yes' или 'off/no'!")
        return ""


WELC_HELP_TXT = "Приветственные/прощальные сообщения вашей группы можно персонализировать разными способами. Если вам нужны сообщения "\
                "для индивидуальной генерации, как и приветственное сообщение по умолчанию, вы можете использовать * эти * переменные:\n" \
                " - `{{first}}`: это представляет пользователя *first* имя\n" \
                " - `{{last}}`: это представляет пользователя *last*. По умолчанию *first name*, если у пользователя нет " \
                "last name.\n" \
                " - `{{fullname}}`: это представляет пользователя *full*. По умолчанию * имя *, если у пользователя нет " \
                "last name.\n" \
                " - `{{username}}`: это представляет пользователя *username*. По умолчанию * упоминание * пользователя" \
                "имя, если нет имени пользователя.\n" \
                " - `{{mention}}`: это просто * упоминает * пользователя, отмечая его именем.\n" \
                " - `{{id}}`: это представляет пользователя *id*\n" \
                " - `{{count}}`: это представляет пользователя *member number*.\n" \
                " - `{{chatname}}`: это представляет собой *текущее имя чата*.\n" \
                "\nКаждая переменная ДОЛЖНА быть окружена символом `{{}}` для замены.\n" \
                "Приветственные сообщения также поддерживают markdown, поэтому вы можете создавать любые элементы. bold/italic/code/links. " \
                "Кнопки также поддерживаются, так что вы можете сделать свое приветствие потрясающим с помощью красивого вступления. " \
                "кнопки.\n" \
                "Чтобы создать кнопку, ссылающуюся на ваши правила, используйте это: `[Rules](buttonurl://t.me/{}?start=group_id)`. " \
                "Вы можете даже установить images/gifs/videos/voice сообщения в качестве приветственного сообщения.".format(dispatcher.bot.username)


@run_async
@user_admin
def welcome_help(bot: Bot, update: Update):
    update.effective_message.reply_text(WELC_HELP_TXT, parse_mode=ParseMode.MARKDOWN)


# TODO: get welcome data from group butler snap
# def __import_data__(chat_id, data):
#     welcome = data.get('info', {}).get('rules')
#     welcome = welcome.replace('$username', '{username}')
#     welcome = welcome.replace('$name', '{fullname}')
#     welcome = welcome.replace('$id', '{id}')
#     welcome = welcome.replace('$title', '{chatname}')
#     welcome = welcome.replace('$surname', '{lastname}')
#     welcome = welcome.replace('$rules', '{rules}')
#     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    welcome_pref, _, _ = sql.get_welc_pref(chat_id)
    goodbye_pref, _, _ = sql.get_gdbye_pref(chat_id)
    return "В этом чате для приветствия установлено значение `{}`.\n" \
           "А для прощания установлено значение`{}`.".format(welcome_pref, goodbye_pref)


__help__ = """
{}

*Только админам:*
 - /welcome <on/off>: включить/выключить приветственное сообщение.
 - /welcome: показывает текущие настройки приветствия.
 - /welcome noformat: показывает текущие настройки приветствия, без форматирования - полезно переработать приветственные сообщения!
 - /goodbye -> такое же использование и аргументы, как /welcome.
 - /setwelcome <sometext>: установить собственное приветственное сообщение. Если используется для ответа на медиа, использует этот медиа.
 - /setgoodbye <sometext>: установить собственное прощальное сообщение. Если используется для ответа на медиа, использует этот медиа.
 - /resetwelcome: Установить стандартное приветсвенное сообщение.
 - /resetgoodbye: установить стандартное прощальное сообщение..
 - /cleanwelcome <on/off>: На новом участнике попробуйте удалить предыдущее приветственное сообщение, чтобы избежать спама в чате.
 - /welcomehelp: просмотреть дополнительную информацию о форматировании пользовательских приветственных/прощальных сообщений.
""".format(WELC_HELP_TXT)

__mod_name__ = "Приветствие\Прощание"

NEW_MEM_HANDLER = MessageHandler(Filters.status_update.new_chat_members, new_member)
LEFT_MEM_HANDLER = MessageHandler(Filters.status_update.left_chat_member, left_member)
WELC_PREF_HANDLER = CommandHandler("welcome", welcome, pass_args=True, filters=Filters.group)
GOODBYE_PREF_HANDLER = CommandHandler("goodbye", goodbye, pass_args=True, filters=Filters.group)
SET_WELCOME = CommandHandler("setwelcome", set_welcome, filters=Filters.group)
SET_GOODBYE = CommandHandler("setgoodbye", set_goodbye, filters=Filters.group)
RESET_WELCOME = CommandHandler("resetwelcome", reset_welcome, filters=Filters.group)
RESET_GOODBYE = CommandHandler("resetgoodbye", reset_goodbye, filters=Filters.group)
CLEAN_WELCOME = CommandHandler("cleanwelcome", clean_welcome, pass_args=True, filters=Filters.group)
WELCOME_HELP = CommandHandler("welcomehelp", welcome_help)

dispatcher.add_handler(NEW_MEM_HANDLER)
dispatcher.add_handler(LEFT_MEM_HANDLER)
dispatcher.add_handler(WELC_PREF_HANDLER)
dispatcher.add_handler(GOODBYE_PREF_HANDLER)
dispatcher.add_handler(SET_WELCOME)
dispatcher.add_handler(SET_GOODBYE)
dispatcher.add_handler(RESET_WELCOME)
dispatcher.add_handler(RESET_GOODBYE)
dispatcher.add_handler(CLEAN_WELCOME)
dispatcher.add_handler(WELCOME_HELP)
