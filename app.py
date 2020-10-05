from flask import Flask, flash, request, redirect, render_template, session
from models import db, connect_db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'somesecretkey'

connect_db(app)

@app.route('/')
def index():
    return render_template('index.html')