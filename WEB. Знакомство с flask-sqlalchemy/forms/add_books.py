from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class BooksForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField("Автор")
    genre = StringField("Жанр")
    img = StringField("Название картинки")
    date = DateField("Дата выдачи")
    status = BooleanField('В наличии')
    submit = SubmitField('Применить')
