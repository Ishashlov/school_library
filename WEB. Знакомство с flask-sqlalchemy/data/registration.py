from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    surname = StringField('surname', validators=[DataRequired()])
    clas = StringField('clas', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    address = StringField('login', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    password_repeat = PasswordField('repeat password', validators=[DataRequired()])
    submit = SubmitField('submit')


