from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, ValidationError
from flask_login import current_user
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Імʼя користувача', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Про себе', validators=[Optional(), Length(max=500)])
    firstname = StringField('Імʼя', validators=[Optional(), Length(max=80)])
    lastname = StringField('Прізвище', validators=[Optional(), Length(max=80)])
    age = StringField('Вік', validators=[Optional(), Length(max=10)])
    gender = SelectField('Стать', choices=[('', '---'), ('M', 'Male'), ('F', 'Female')],
                         validators=[Optional()])
    address = StringField('Адреса', validators=[Optional(), Length(max=200)])
    website = StringField('Вебсайт', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Зберегти')

    def validate_username(self, field):
        if field.data != current_user.username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('Це імʼя вже зайняте.')

    def validate_email(self, field):
        if field.data.lower() != current_user.email:
            if User.query.filter_by(email=field.data.lower()).first():
                raise ValidationError('Цей email вже використовується.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Поточний пароль', validators=[DataRequired()])
    new_password = PasswordField('Новий пароль', validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField('Підтвердіть новий пароль',
                                  validators=[DataRequired(),
                                              EqualTo('new_password',
                                                      message='Паролі не співпадають')])
    submit = SubmitField('Змінити пароль')