# Blueprint for reader module

from flask import Blueprint, render_template, request
from models import UserBook, db
from os.path import join
from app import app
from flask_login import login_required, current_user
from datetime import datetime

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
    book.last_read = datetime.now()
    try:
        db.session.add(book)
        db.session.commit()
    except:
        pass

    return render_template('reader.html')