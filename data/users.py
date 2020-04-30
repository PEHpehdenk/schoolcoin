import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
import sqlalchemy.orm as orm
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import db


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    schoolcoins = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    numberoftasks = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    olimps = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    averagemark = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    news = orm.relation("News", back_populates='user')
    tasks = orm.relation("Tasks", back_populates='user')
    vacancys = orm.relation("Vacancys", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
