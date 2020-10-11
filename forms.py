from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Length, DataRequired, Email

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