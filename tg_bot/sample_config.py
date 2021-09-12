if not __name__.endswith("sample_config"):
    import sys
    print("README должен быть прочитан. Расширьте этот образец конфигурации до файла конфигурации, а не просто переименуйте и измените "
          "значения здесь. Это будет иметь неприятные последствия для вас. \nБот завершает свою работу.", file=sys.stderr)
    quit(1)



# Создать новый файл config.py в том же каталоге и импортировать, а затем расширить этот класс.
class Config(object):

    
    LOGGER = True

    # Обязательно
    API_KEY = ""
    OWNER_ID = ""  # Если не знаешь свой id напиши в личном чате в боте \id
    OWNER_USERNAME = ""
    CHAT_ID = ""

    # RECOMMENDED
    SQLALCHEMY_DATABASE_URI = ''  # необходим для любых модулей базы данных
    MESSAGE_DUMP = False  # необходимо, чтобы сообщения "сохранить из" сохранялись
    LOAD = []
    NO_LOAD = [] # Список не загружаемых модулей
    WEBHOOK = False
    URL = None

    # OPTIONAL
    SUDO_USERS = []  # Список идентификаторов (не имен пользователей) для пользователей, у которых есть доступ sudo к боту.
    SUPPORT_USERS = []  # Список идентификаторов (не имен пользователей) для пользователей, которым разрешено использовать gban, но которые также могут быть забанены.
    WHITELIST_USERS = []  # Список идентификаторов (не имен пользователей) для пользователей, которые НЕ БУДУТ забанены / кикнуты ботом.
    DONATION_LINK = None  # EG, paypal
    CERT_PATH = None
    PORT = 5000
    DEL_CMDS = False  # Whether or not you should delete "blue text must click" commands
    STRICT_GBAN = False
    WORKERS = 8  # Количество используемых субпотоков. Это рекомендуемая сумма - посмотрите сами, что работает лучше всего!
    BAN_STICKER = 'CAADAgADOwADPPEcAXkko5EB3YGYAg'  # Стикер для бана
    ALLOW_EXCL = False # Запускать ! команды, а также /


class Production(Config):
    LOGGER = False


class Development(Config):
    LOGGER = True
