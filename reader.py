# Blueprint for reader module

from flask import Blueprint, render_template
from os.path import join
from app import app

reader_path = join(app.root_path, 'reader/reader')
reader = Blueprint('reader', __name__, static_folder=reader_path)

@reader.route('/')
def reader_view():
    # TODO: Pass in google drive book handle
    return render_template('reader.html')