from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Імʼя користувача',
                           validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Підтвердіть пароль',
                              validators=[DataRequired(), EqualTo('password',
                                          message='Паролі не співпадають')])
    submit = SubmitField('Зареєструватися')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Це імʼя вже зайняте. Оберіть інше.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Цей email вже зареєстрований.')


class LoginForm(FlaskForm):
    username = StringField('Імʼя користувача', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запамʼятати мене')
    submit = SubmitField('Увійти')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Надіслати посилання для скидання')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новий пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Підтвердіть новий пароль',
                              validators=[DataRequired(), EqualTo('password',
                                          message='Паролі не співпадають')])
    submit = SubmitField('Змінити пароль')
