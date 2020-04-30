import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Tasks(SqlAlchemyBase):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    asnwer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    cost = sqlalchemy.Column(sqlalchemy.Integer, default=5, nullable=False)
    reusable = sqlalchemy.Column(sqlalchemy.Integer, default=1000, nullable=False)
    answeroftask = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    correctUsers = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user = orm.relation('User')
    categories = orm.relation("Category",
                              secondary="association",
                              backref="tasks")