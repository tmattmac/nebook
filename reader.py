# Blueprint for reader module

from flask import Blueprint, render_template, request
from models import UserBook
from os.path import join
from app import app
from flask_login import login_required, current_user

reader_path = join(app.root_path, 'reader/reader')
reader = Blueprint('reader', __name__, static_folder=reader_path)

@reader.route('/<book_id>')
@login_required
def reader_view(book_id):
    # ensure book exists
    book = UserBook.query.get_or_404({
        'user_id': current_user.id,
        'gdrive_id': book_id
    })
    # TODO: Pass in google drive book handle
    return render_template('reader.html')