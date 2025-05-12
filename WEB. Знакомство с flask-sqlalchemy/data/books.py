import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import create_session

from .db_session import SqlAlchemyBase


class Books(SqlAlchemyBase):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    img = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    reader = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    copies_available = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    total_copies = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def take_book(self, user):
        if self.copies_available > 0:
            self.copies_available -= 1
            if self.copies_available == 0:
                self.status = False
            self.reader = f"{user.surname} {user.name}"
            self.date = datetime.date.today()
            return True
        return False

    def return_book(self):
        self.copies_available += 1
        if self.copies_available > 0:
            self.status = True
        if self.copies_available == self.total_copies:  # предполагая, что total_copies - это общее количество копий
            self.reader = None
            self.date = None

    def can_take_book(self, user):
        """Проверка возможности взять книгу с гарантированным возвратом кортежа"""
        try:
            if not hasattr(user, 'surname') or not hasattr(user, 'name'):
                return (False, "Недостаточно данных пользователя")

            if self.copies_available <= 0:
                return (False, "Все экземпляры уже выданы")

            if self.reader == f"{user.surname} {user.name}":
                return (False, "Вы уже взяли этот экземпляр")

            db_sess = create_session()
            same_book_taken = db_sess.query(Books).filter(
                Books.title == self.title,
                Books.author == self.author,
                Books.reader == f"{user.surname} {user.name}"
            ).first()

            if same_book_taken:
                return (False, "Вы уже взяли другой экземпляр этой книги")

            return (True, "Можно взять книгу")

        except Exception as e:
            return (False, f"Ошибка проверки: {str(e)}")
