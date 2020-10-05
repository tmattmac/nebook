from flask import Flask, flash, request, redirect, render_template, session
from models import db, connect_db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'somesecretkey'

connect_db(app)

from reader import reader
app.register_blueprint(reader, url_prefix='/reader')

@app.route('/')
def index():
    return render_template('index.html')