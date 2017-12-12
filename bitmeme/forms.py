from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, FileField
from wtforms.validators import (DataRequired, Regexp, Email, ValidationError,
                                Length, EqualTo)

from models import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists')


class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z-0-9_.]+$',
                message=('Username should be one word, letters,'
                         ' numbers, periods, and underscores only')),
            name_exists,
        ])
    email = StringField(
        'Email', validators=[
            DataRequired(),
            Email(),
            email_exists,
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class PostForm(Form):
    image = FileField(validators=[DataRequired()])
    content = TextAreaField(
        'Meme description (250 char max)',
        validators=[DataRequired(), Length(max=250)])


class CommentForm(Form):
    content = TextAreaField(
        'Comment (250 char max)', validators=[DataRequired(),
                                              Length(max=250)])
