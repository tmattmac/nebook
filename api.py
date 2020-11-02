from flask import request, jsonify, Blueprint, session, send_file
from flask_login import current_user, login_required
from app import app
from models import *
import gdrive
import gauth
from helpers import build_query, get_authors, get_tags

ajax = Blueprint('ajax', __name__)

@ajax.route('/books')
@login_required
def get_books():
    
    result, count = build_query(current_user, **request.args)
    output = {
        'count': count,
        'results': [serialize_book(book) for book in result]
    }
    return jsonify(output)

@ajax.route('/books/<book_id>')
@login_required
def get_single_book(book_id):
    book = UserBook.query.get_or_404({
        'user_id': current_user.id,
        'gdrive_id': book_id
    })
    return jsonify(serialize_book(book))

@ajax.route('/tags')
@login_required
def get_user_tags():
    tags = get_authors(current_user.id)
    return jsonify({
        'tags': [{
            'id': tag.id,
            'name': tag.tag_name
        } for tag in tags]
    })

@ajax.route('/authors')
@login_required
def get_user_authors():
    authors = get_authors(current_user.id)
    return jsonify({
        'authors': [{
            'id': author.id,
            'name': author.name
        } for author in authors]
    })

@ajax.route('/book/<book_id>/progress', methods=['GET', 'POST'])
@login_required
def book_progress(book_id):

    book = UserBook.query.get_or_404({
        'user_id': current_user.id,
        'gdrive_id': book_id
    })

    if request.method == 'POST':
        try:
            progress = request.json.get('progress', book.progress_percentage)
            book.progress_percentage = float(progress)
            db.session.add(book)
            db.session.commit()
        except:
            return jsonify({'error': 'Could not update progress'})

    return jsonify({
        'progress': book.progress_percentage
    })
    

@ajax.route('/book/file/<book_id>.epub')
@login_required
def get_book_file(book_id):

    # Make sure book exists
    book = UserBook.query.get_or_404({
        'user_id': current_user.id,
        'gdrive_id': book_id
    })

    credentials = gauth.create_credentials(
        user=current_user,
        access_token=session.get('access_token')
    )
    
    file = gdrive.download_file(credentials, book_id)

    # TODO: Find way to invalidate cache if user deletes file
    return send_file(file, mimetype='application/epub+zip', cache_timeout=7 * 24 * 60 * 60)

def serialize_book(book):
    return {
        'title': book.title,
        'gdrive_id': book.gdrive_id,
        'publisher': book.publisher,
        'publication_year': book.publication_year,
        'authors': [{
            'id': author.id,
            'name': author.name
        } for author in book.authors],
        'tags': [{
            'id': tag.id,
            'name': tag.tag_name
        } for tag in book.tags],
        'comments': book.comments,
        'cover_image': book.cover_image,
        'last_read': book.last_read
    }