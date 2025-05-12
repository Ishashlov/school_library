from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class BooksForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    genre = StringField('Жанр', validators=[DataRequired()])
    img = StringField('Обложка (имя файла)')
    total_copies = IntegerField('Количество копий', default=1, validators=[DataRequired()])
    status = BooleanField('Доступна', default=True)
    submit = SubmitField('Сохранить')
