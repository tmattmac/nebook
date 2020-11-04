# Blueprint for reader module

from flask import Blueprint, render_template, request, session, redirect, url_for
from models import UserBook, db
from os.path import join
from app import app
from flask_login import login_required, current_user
from datetime import datetime
import google
import gauth

reader_path = join(app.root_path, 'reader/reader')
reader = Blueprint('reader', __name__, static_folder=reader_path)

@reader.route('/<book_id>')
@login_required
def reader_view(book_id):

    try:
        credentials = gauth.create_credentials(
            user=current_user,
            access_token=session.get('access_token')
        )
    except google.auth.exceptions.RefreshError as error:
        return redirect(url_for('gdrive_acknowledge'))

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
        db.session.rollback()

    return render_template('reader.html', book=book)