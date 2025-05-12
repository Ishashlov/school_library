from flask import Flask, render_template, redirect, abort, request
from flask_login import (LoginManager, login_user, login_required,
                         logout_user, current_user)

from data import db_session

import jinja2

from data.users import User
from data.news import News
from data.books import Books
from forms.registration import RegisterForm
from forms.login import LoginForm
from forms.add_news import NewsForm
from forms.add_books import BooksForm
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


# @app.route("/")
# def home():
#     authors = ["Пушкин", "Толстой", "Грибоедов", "Фет", "Блок"]
#     genres = [
#         "Проза", "Поэзия", "Роман", "Рассказ", "Новелла", "Научная фантастика", "Приключения",
#         "Романтика", "Драма", "Эссе", "Мемуары", "Философия", "Биография", "Фэнтези",
#         "Исторический роман", "Повесть", "Бизнес", "Кулинарные книги"
#     ]
#     return render_template("books.html", authors=authors, genres=genres, username=session.get('username'))


@login_manager.user_loader
def Load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_repeat.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            clas=form.clas.data,
            email=form.email.data,
            login=form.login.data,
            hashed_password=form.password.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()
    return render_template("index.html", news=news)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('add_news.html', title='Добавление новости',
                           form=form)


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/books')
def books():
    db_sess = db_session.create_session()
    books = db_sess.query(Books).all()
    return render_template("books.html", books=books)


@app.route('/add_books', methods=['GET', 'POST'])
@login_required
def add_books():
    form = BooksForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = Books(
            title=form.title.data,
            author=form.author.data,
            genre=form.genre.data,
            img=form.img.data,
            total_copies=form.total_copies.data,
            copies_available=form.total_copies.data,
            user_id=current_user.id
        )
        db_sess.add(book)
        db_sess.commit()
        return redirect('/books')
    return render_template('add_books.html', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/books/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_books(id):
    form = BooksForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        books = db_sess.query(Books).filter(Books.id == id,
                                            Books.user == current_user).first()
        if books:
            print(books.reader)
            form.title.data = books.title
            form.author.data = books.author
            form.genre.data = books.genre
            form.status.data = books.status
            form.img.data = books.img
            form.date.data = books.date
            form.reader = books.reader
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        books = db_sess.query(Books).filter(Books.id == id,
                                            Books.user == current_user).first()
        if books:
            books.title = form.title.data
            books.author = form.author.data
            books.genre = form.genre.data
            books.status = form.status.data
            books.img = form.img.data
            books.date = form.date.data
            books.reader = form.reader
            db_sess.commit()
            return redirect('/books')
        else:
            abort(404)
    return render_template('add_books.html',
                           title='Редактирование книги',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/read/<filename>')
def read_book(filename):
    return render_template('read_book.html', filename=filename)


@app.route('/take_book/<int:book_id>', methods=['POST'])
@login_required
def take_book(book_id):
    db_sess = db_session.create_session()

    # Используем современный метод query.get() -> session.get()
    book = db_sess.get(Books, book_id)  # Изменено здесь

    if not book:
        return redirect('/books')

    # Добавляем проверку возвращаемого значения
    result = book.can_take_book(current_user)
    if result is None or not isinstance(result, tuple) or len(result) != 2:
        return redirect('/books')

    can_take, message = result

    if not can_take:
        return redirect('/books')

    # Обработка взятия книги
    try:
        book.copies_available -= 1
        book.reader = f"{current_user.surname} {current_user.name}"
        book.date = datetime.date.today()

        if book.copies_available == 0:
            book.status = False

        db_sess.commit()
    except Exception as e:
        db_sess.rollback()

    return redirect('/books')


@app.route('/return_book/<int:book_id>', methods=['POST'])
@login_required
def return_book(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Books).get(book_id)

    if not book:
        abort(404)

    if book.reader == f"{current_user.surname} {current_user.name}":
        book.copies_available += 1
        if book.copies_available == book.total_copies:
            book.reader = None
            book.date = None
        db_sess.commit()

    return redirect('/books')


@app.route('/books_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def books_delete(id):
    db_sess = db_session.create_session()
    books = db_sess.query(Books).filter(Books.id == id).first()
    if books:
        db_sess.delete(books)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/books')


def main():
    db_session.global_init("db/school_library.db")
    db_session.apply_migrations()
    app.run(port=4000)


if __name__ == '__main__':
    main()
