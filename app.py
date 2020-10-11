from flask import Flask, flash, request, redirect, render_template, session
from models import db, connect_db
from flask_login import LoginManager
from models import *

app = Flask(__name__)
login_manager = LoginManager()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'somesecretkey'

connect_db(app)
login_manager.init_app(app)

import auth
from reader import reader
app.register_blueprint(reader, url_prefix='/reader')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')