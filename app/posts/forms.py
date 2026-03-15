from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), Length(min=3, max=200)])
    description = StringField('Короткий опис', validators=[DataRequired(), Length(min=3, max=500)])
    body = TextAreaField('Текст запису', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Опублікувати')


class CommentForm(FlaskForm):
    name = StringField('Імʼя', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('Повідомлення', validators=[DataRequired(), Length(min=1, max=2000)])
    submit = SubmitField('Додати коментар')
