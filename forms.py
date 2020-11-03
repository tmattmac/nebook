from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, SelectField, HiddenField, SelectMultipleField
from lib.wtf_taglist import TagListField
from wtforms.widgets.core import HTMLString, html_params
from wtforms.validators import Length, DataRequired, Email, NumberRange
from datetime import datetime

class UserLoginForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[DataRequired('Username is required')]
    )

    password=PasswordField(
        'Password',
        validators=[DataRequired('Password is required'), Length(min=8)]
    )

class UserRegisterForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[DataRequired('Username is required')]
    )

    email = StringField(
        'Email address',
        validators=[DataRequired('Email is required'), Email()]
    )

    password=PasswordField(
        'Password',
        validators=[DataRequired('Password is required'), Length(min=8)]
    )

class EditBookDetailForm(FlaskForm):

    title = StringField(
        'Title',
        validators=[DataRequired()]
    )

    authors = TagListField('Authors', separator=',')

    publisher = StringField('Publisher')

    publication_year = IntegerField(
        'Publication Year',
        validators=[NumberRange(min=0, max=datetime.now().year)]
    )

    comments = TextAreaField('Comments')

    cover_image = StringField('Cover Image URL')

    tags = TagListField('Tags', separator=',')

class BookSearchForm(FlaskForm):

    q = StringField()
    sort = SelectField(choices=[
        ('last_read', 'Last Read'),
        ('title', 'Title'),
        ('publisher', 'Publisher'),
        ('publication_year', 'Year'),
        ('author', 'Author')
    ])

    author = SelectMultipleField('Author(s)', coerce=int)
    tag = SelectMultipleField('Tag(s)', coerce=int)