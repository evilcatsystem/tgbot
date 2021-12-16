from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
# from sqlalchemy.pool import NullPool, Pool

from tg_bot import DB_URI


def start() -> scoped_session:
    engine = create_engine(DB_URI, encoding='utf8')
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = start()
