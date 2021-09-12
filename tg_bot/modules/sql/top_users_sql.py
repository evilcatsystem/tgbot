from sqlalchemy import Column, UnicodeText, Integer, desc, cast

from tg_bot.modules.sql import BASE, SESSION

class top_sql(BASE):
    __tablename__ = "top_users"
    user_id = Column(Integer, primary_key=True)
    name = Column(UnicodeText)
    message = Column(Integer)

    def __init__(self, user_id, name, message):
        self.user_id = user_id
        self.name = name
        self.message = message

    def __repr__(self):
        result = '{} {} '.format(self.name, self.message)
        return result


top_sql.__table__.create(checkfirst=True)

def set_top(user_id, message):
    try:
        for row in SESSION.query(top_sql).filter(top_sql.user_id == user_id):
            row.message = message
            SESSION.add(row)
        SESSION.commit()
    finally:
        SESSION.close()


def user_list_top():
    try:
        rows = SESSION.query(top_sql).order_by(desc(cast(top_sql.message, Integer))).all()
        return rows
    finally:
        SESSION.close()


def write_top(user_id, name):
    try:
        for row in SESSION.query(top_sql).filter(top_sql.user_id == user_id):
            mes = int(row.message) + int(1)
            result = mes
            row.name = name
            row.message = result
            SESSION.add(row)
        SESSION.commit()
    finally:
        SESSION.close()

def get_user_top(user_id, name):
    try:
        objects = [top_sql(user_id=user_id, name=name, message=1)]
        SESSION.add_all(objects)
        SESSION.commit()
    finally:
        SESSION.close()

def delete_user_top(user_id):
    try:
        user = SESSION.query(top_sql).get(user_id)
        if user:
            SESSION.delete(user)

        SESSION.commit()
    finally:
        SESSION.close()


