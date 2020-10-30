from flask import request, jsonify, Blueprint, session, send_file
from flask_login import current_user, login_required
from sqlalchemy import or_, desc, func
from app import app
from models import *
import gdrive
import gauth

ajax = Blueprint('ajax', __name__)

def build_query(**kwargs):
    """
    Build a query on books based on provided query parameters
    q       search query (not yet implemented)
    pg      page of results (default: 1)
    per_pg  number of results to show per page (default: 20)
    author  filter by author with specified id
    sort    name of column to sort by (default: title)
    """
    SORT_FIELDS = ['title', 'publisher', 'publication_year', 'last_read', 'author']

    # TODO: Get items per page from user preferences
    # TODO: Add tag filtering
    pg = kwargs.get('pg', 1) - 1
    per_pg = kwargs.get('per_pg', 20)
    sort = kwargs.get('sort')
    order = kwargs.get('order')
    author = kwargs.get('author')
    tag = kwargs.get('tag')
    q = kwargs.get('q')
    publisher = kwargs.get('publisher')
    year = kwargs.get('year')

    query = db.session.query(UserBook)\
        .filter(UserBook.user_id == current_user.id)\
        .outerjoin(UserBook.authors)\
        .outerjoin(UserBook.tags)

    if author:
        query = query.filter(Author.id == author)
    if tag:
        query = query.filter(Tag.id == tag)
    if publisher:
        query = query.filter(UserBook.publisher.ilike(f'%{publisher}%'))
    if year:
        query = query.filter(UserBook.publication_year == year)

    if q:
        q = f'%{q}%'
        query = query.filter(or_(
            UserBook.title.ilike(q),
            UserBook.publisher.ilike(q),
            Tag.tag_name.ilike(q),
            Author.name.ilike(q)
        ))

    if not sort or sort not in SORT_FIELDS:
        sort = 'last_read'
        order = 'desc'
    elif sort == 'author':
        sort = Author.name

    if order == 'desc':
        query = query.order_by(desc(sort))
    else:
        query = query.order_by(sort)

    count = query.count()

    query = query\
            .limit(per_pg)\
            .offset(pg * per_pg)

    return query.all(), count

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

@ajax.route('/books')
@login_required
def get_books():
    
    result, count = build_query(**request.args)
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
    tags = db.session.query(Tag)\
        .filter(Tag.user_id==current_user.id)\
        .join(Tag.books)\
        .all()
    return jsonify({
        'tags': [{
            'id': tag.id,
            'name': tag.tag_name
        } for tag in tags]
    })

@ajax.route('/authors')
@login_required
def get_user_authors():
    authors = db.session.query(Author)\
        .filter(Author.user_id==current_user.id)\
        .join(Author.books)\
        .all()
    return jsonify({
        'authors': [{
            'id': author.id,
            'name': author.name
        } for author in authors]
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
    return send_file(file, mimetype='application/epub+zip', cache_timeout=7*24*60*60)