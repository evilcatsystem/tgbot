import logging
import os
import sys

import telegram.ext as tg

# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    LOGGER.error("У вас ДОЛЖНА быть версия Python не ниже 3.6! От этого зависят несколько функций. Бот завершает работу.")
    quit(1)

ENV = bool(os.environ.get('ENV', False))

if ENV:
    TOKEN = os.environ.get('TOKEN', None)
    try:
        OWNER_ID = int(os.environ.get('OWNER_ID', None))
    except ValueError:
        raise Exception("Ваша переменная env OWNER_ID не является допустимым целым числом.")

    MESSAGE_DUMP = os.environ.get('MESSAGE_DUMP', None)
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", None)

    try:
        SUDO_USERS = set(int(x) for x in os.environ.get("SUDO_USERS", "").split())
    except ValueError:
        raise Exception("Ваш список пользователей sudo не содержит действительных целых чисел.")

    try:
        SUPPORT_USERS = set(int(x) for x in os.environ.get("SUPPORT_USERS", "").split())
    except ValueError:
        raise Exception("В вашем списке пользователей службы поддержки нет действительных целых чисел..")

    try:
        WHITELIST_USERS = set(int(x) for x in os.environ.get("WHITELIST_USERS", "").split())
    except ValueError:
        raise Exception("Список пользователей из белого списка не содержит действительных целых чисел.")

    WEBHOOK = bool(os.environ.get('WEBHOOK', False))
    URL = os.environ.get('URL', "")  # Does not contain token
    PORT = int(os.environ.get('PORT', 5000))
    CERT_PATH = os.environ.get("CERT_PATH")

    DB_URI = os.environ.get('DATABASE_URL')
    DONATION_LINK = os.environ.get('DONATION_LINK')
    LOAD = os.environ.get("LOAD", "").split()
    NO_LOAD = os.environ.get("NO_LOAD", "translation").split()
    DEL_CMDS = bool(os.environ.get('DEL_CMDS', False))
    STRICT_GBAN = bool(os.environ.get('STRICT_GBAN', False))
    WORKERS = int(os.environ.get('WORKERS', 8))
    BAN_STICKER = os.environ.get('BAN_STICKER', 'CAADAgADOwADPPEcAXkko5EB3YGYAg')
    ALLOW_EXCL = os.environ.get('ALLOW_EXCL', False)
    CHAT_ID = os.environ.get('CHAT_ID')

else:
    from tg_bot.config import Development as Config
    TOKEN = Config.API_KEY
    try:
        OWNER_ID = int(Config.OWNER_ID)
    except ValueError:
        raise Exception("Ваша переменная env OWNER_ID не является допустимым целым числом.")

    MESSAGE_DUMP = Config.MESSAGE_DUMP
    OWNER_USERNAME = Config.OWNER_USERNAME

    try:
        SUDO_USERS = set(int(x) for x in Config.SUDO_USERS or [])
    except ValueError:
        raise Exception("Ваш список пользователей sudo не содержит действительных целых чисел.")

    try:
        SUPPORT_USERS = set(int(x) for x in Config.SUPPORT_USERS or [])
    except ValueError:
        raise Exception("В вашем списке пользователей службы поддержки нет действительных целых чисел.")

    try:
        WHITELIST_USERS = set(int(x) for x in Config.WHITELIST_USERS or [])
    except ValueError:
        raise Exception("Список пользователей из белого списка не содержит действительных целых чисел.")

    WEBHOOK = Config.WEBHOOK
    URL = Config.URL
    PORT = Config.PORT
    CERT_PATH = Config.CERT_PATH

    DB_URI = Config.SQLALCHEMY_DATABASE_URI
    DONATION_LINK = Config.DONATION_LINK
    LOAD = Config.LOAD
    NO_LOAD = Config.NO_LOAD
    DEL_CMDS = Config.DEL_CMDS
    STRICT_GBAN = Config.STRICT_GBAN
    WORKERS = Config.WORKERS
    BAN_STICKER = Config.BAN_STICKER
    ALLOW_EXCL = Config.ALLOW_EXCL
    CHAT_ID = Config.CHAT_ID


SUDO_USERS.add()

updater = tg.Updater(TOKEN, workers=WORKERS)

dispatcher = updater.dispatcher

SUDO_USERS = list(SUDO_USERS)
WHITELIST_USERS = list(WHITELIST_USERS)
SUPPORT_USERS = list(SUPPORT_USERS)

# Загружать в конце, чтобы убедиться, что все предыдущие переменные были установлены
from tg_bot.modules.helper_funcs.handlers import CustomCommandHandler, CustomRegexHandler

# убедитесь, что обработчик регулярных выражений может принимать дополнительные аргументы
tg.RegexHandler = CustomRegexHandler

if ALLOW_EXCL:
    tg.CommandHandler = CustomCommandHandler
