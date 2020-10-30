from flask import Flask, flash, request, redirect, render_template, session, url_for, send_file
from flask_login import LoginManager, login_required, current_user
from models import *
import os
from sync import book_model_from_api_data
from forms import EditBookDetailForm, BookSearchForm

import gdrive
import gbooks

app = Flask(__name__)

# TODO: Update config to use env vars
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///book_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'somesecretkey'

# TODO: Disable these in production
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

connect_db(app)

import auth
import gauth

from reader import reader
from services import ajax, build_query
app.register_blueprint(reader, url_prefix='/reader')
app.register_blueprint(ajax, url_prefix='/api')

@app.route('/')
@login_required
def index():
    books, count = build_query(**request.args)

    form = BookSearchForm(
        csrf_enabled=False,
        data=request.args
    )

    session['view'] = request.args.get('view') or session.get('view', 'grid')

    # TODO: Store folder ID in session
    #folderId = gdrive.get_app_folder_id(credentials)
    #files = gdrive.get_all_epub_file_ids(credentials)

    # Test epub opening
    # from lib.epubtag import EpubBook
    # file = gdrive.download_file(credentials, files[0])
    # epub = EpubBook(file)

    return render_template('index.html', books=books, books_count=count, form=form)

@app.route('/book/<book_id>')
@login_required
def book_details(book_id):
    book = UserBook.query.get_or_404({
        'user_id': current_user.id,
        'gdrive_id': book_id
    })
    
    return render_template('book/details.html', book=book)

@app.route('/book/<book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book_details(book_id):
    book = UserBook.query.get_or_404({
        'user_id': current_user.id,
        'gdrive_id': book_id
    })
    form = EditBookDetailForm(obj=book)
    if form.validate_on_submit():
        # TODO: Wrap in try-catch
        update_book_with_form_data(book, form)
        return redirect(url_for('book_details', book_id=book.gdrive_id))

    return render_template('book/edit_details.html', book=book, form=form)

def update_book_with_form_data(book_instance, form):
    book = {
        'title':            form.title.data,
        'publisher':        form.publisher.data,
        'publication_year': form.publication_year.data,
        'comments':         form.comments.data,
        'authors':          [],
        'tags':             []
    }
    for author_name in form.authors.data:
        author = get_or_create(Author, name=author_name, user_id=current_user.id)
        book['authors'].append(author)
    for tag_name in form.tags.data:
        tag = get_or_create(Tag, tag_name=tag_name, user_id=current_user.id)
        book['tags'].append(tag)

    for k, v in book.items():
        setattr(book_instance, k, v)

    db.session.add(book_instance)
    db.session.commit()

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_ebook_file():
    
    if not current_user.gdrive_permission_granted:
        return redirect(url_for('index'))
        
    if request.method == 'GET':
        return render_template('book/upload.html')

    credentials = gauth.create_credentials(
        user=current_user,
        access_token=session.get('access_token')
    )

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
        flash('Not a valid ebook file', 'danger')
        return redirect(url_for('upload_ebook_file'))

    book_info = gbooks.get_book_by_title_author(title, author)

    #--------------DISABLED FOR DEVELOPMENT------------------------------------
    book_gdrive_id = gdrive.generate_file_id(credentials)
    gdrive.upload_file(credentials, file, f'{title} - {author}', gdrive.get_app_folder_id(credentials), book_gdrive_id)
    # book_gdrive_id = str(current_user.id) + book_info.get('id')
    #--------------------------------------------------------------------------

    book = book_model_from_api_data(current_user.id, book_info)
    book.gdrive_id = book_gdrive_id
    db.session.add(book)
    db.session.commit()

    return redirect(url_for('edit_book_details', book_id=book.gdrive_id))
