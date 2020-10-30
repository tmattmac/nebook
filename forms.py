from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, SelectField, HiddenField
from lib.wtf_taglist import TagListField
from wtforms.validators import Length, DataRequired, Email, NumberRange
from datetime import datetime

class UserLoginForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[DataRequired()]
    )

    password=PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)]
    )

class UserRegisterForm(FlaskForm):

    username = StringField(
        'Username',
        validators=[DataRequired()]
    )

    email = StringField(
        'Email address',
        validators=[DataRequired(), Email()]
    )

    password=PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)]
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