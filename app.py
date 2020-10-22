from flask import Flask, flash, request, redirect, render_template, session, url_for
from models import db, connect_db
from sqlalchemy import desc
from flask_login import LoginManager, login_required, current_user
from models import *
import os
from sync import book_model_from_api_data

# TODO: Refactor Gdrive functions to new file
import google.oauth2.credentials
import google_auth_oauthlib.flow
import gdrive
import gbooks

app = Flask(__name__)

# TODO: Update config to use env vars
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///book_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'somesecretkey'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # TODO: Disable in production


connect_db(app)
db.create_all()

import auth

from reader import reader
app.register_blueprint(reader, url_prefix='/reader')

def build_query(**kwargs):
    """
    Build a query on books based on provided query parameters
    q       search query (not yet implemented)
    pg      page of results (default: 1)
    per_pg  number of results to show per page (default: 20)
    author  filter by author with specified id
    sort    name of column to sort by (default: title)
    """
    # TODO: Get items per page from user preferences
    pg = kwargs.get('pg', 1) - 1
    per_pg = kwargs.get('per_pg', 20)
    sort = kwargs.get('sort', 'title')
    order = kwargs.get('order', 'asc')
    author = kwargs.get('author')

    if author:
        query = db.session.query(UserBook).join(UserBook.authors).filter(Author.id==author)
    else:
        query = UserBook.query

    if sort not in UserBook.__table__.columns.keys():
        sort = 'title'

    if order == 'desc':
        query = query.order_by(desc(sort))
    else:
        query = query.order_by(sort)

    count = query.count()

    query = query\
            .limit(per_pg)\
            .offset(pg * per_pg)

    return query.all(), count

@app.route('/')
@login_required
def index():
    if 'credentials' not in session:
        return redirect(url_for('gdrive_authorize'))

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])

    books, count = build_query(**request.args)

    # TODO: Store folder ID in session
    #folderId = gdrive.get_app_folder_id(credentials)
    #files = gdrive.get_all_epub_file_ids(credentials)

    # Test epub opening
    # from lib.epubtag import EpubBook
    # file = gdrive.download_file(credentials, files[0])
    # epub = EpubBook(file)

    return render_template('index.html', books=books, books_count=count)

@app.route('/upload', methods=['POST'])
@login_required
def upload_ebook_file():
    if 'credentials' not in session:
        return redirect(url_for('gdrive_authorize'))

    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])

    file = request.files['file']

    from lib.epubtag import EpubBook
    epub = EpubBook(file)
    try:
        title = epub.get_title()
        authors = epub.get_authors()
        author = ''
        if len(authors) > 0:
            author = authors[0]
    except RuntimeError:
        return redirect(url_for('index'))

    book_info = gbooks.get_book_by_title_author(title, author)

    #--------------DISABLED FOR DEVELOPMENT------------------------------------
    # book_gdrive_id = gdrive.generate_file_id(credentials)
    # gdrive.upload_file(credentials, file, f'{title} - {author}', gdrive.get_app_folder_id(credentials), book_gdrive_id)
    book_gdrive_id = book_info.get('id')
    #--------------------------------------------------------------------------

    book = book_model_from_api_data(current_user.id, book_info)
    book.gdrive_id = book_gdrive_id
    db.session.add(book)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/gdrive-authorize')
@login_required
def gdrive_authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=[
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/drive.file'
        ]
    )

    flow.redirect_uri = url_for('gdrive_callback', _external=True)  # TODO: Change this
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state

    return redirect(auth_url)

@app.route('/gdrive-authorize-callback')
def gdrive_callback():

    # TODO: Confirm request url is from Google oauth page, redirect if not
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=[
            'https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/drive.file'
        ],
        state=state
    )

    flow.redirect_uri = url_for('gdrive_callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    # Store refresh token in database
    current_user.gdrive_permission_granted = True
    current_user.gdrive_refresh_token = credentials.refresh_token
    db.session.add(current_user)
    try:
        db.session.commit()
    except:
        # TODO: Handle database errors
        pass
    return redirect(url_for('index'))