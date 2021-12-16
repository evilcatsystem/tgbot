import threading

from sqlalchemy import Column, UnicodeText, Boolean, Integer

from tg_bot.modules.sql import BASE, SESSION


class MES(BASE):
    __tablename__ = "mess"

    mes = Column(UnicodeText, primary_key=True)

    def __init__(self, mes):
        self.mes = mes
        
    def __repr__(self):
        result = '{}'.format(self.mes)
        return result

MES.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

def write_message(mes):
    try:
        row = MES(mes=mes)
        SESSION.add(row)
        SESSION.commit()
    finally:
        SESSION.close()

def delete_message(mes):
    try:
        user = SESSION.query(MES).get(mes)
        if user:
            SESSION.delete(user)

        SESSION.commit()
    finally:
        SESSION.close()

def get_message():
    try:
        rows = SESSION.query(MES).all()
        return rows
    finally:
        SESSION.close()
