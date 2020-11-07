from flask import Flask, flash, request, redirect, render_template, session, url_for, send_file
from flask_login import LoginManager, login_required, current_user
from models import *
import os
from forms import EditBookDetailForm, BookSearchForm
from helpers import *
import google
import gdrive
import gbooks
import secrets

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///book_project')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'somesecretkey')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# TODO: Disable these in production
# app.config['SQLALCHEMY_ECHO'] = True
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

connect_db(app)

# Routes in external files
import auth
import gauth
from reader import reader
from api import ajax
app.register_blueprint(reader, url_prefix='/reader')
app.register_blueprint(ajax, url_prefix='/api')


@app.route('/')
@login_required
def index():

    # TODO: Populate form only if user searched
    ref_search = True if request.args.get('ref') == 'search' else False
    form = BookSearchForm(
        formdata=request.args,
        meta={'csrf': False}
    )

    try:
        pg = int(request.args['pg'])
    except:
        pg = 1
    books, search_meta = build_query(
        current_user,
        pg=pg,
        **form.data
    )

    # TODO: Cache these somehow
    form.author.choices = [(a.id, a.name) for a in get_authors(current_user.id)]
    form.tag.choices = [(t.id, t.tag_name) for t in get_tags(current_user.id)]

    session['view'] = request.args.get('view') or session.get('view', 'grid')

    return render_template(
        'index.html',
        books=books.items,
        pagination=books,
        search_meta=search_meta,
        form=form,
        ref_search=ref_search
    )

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


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_ebook_file():
    
    try:
        credentials = gauth.create_credentials(
            user=current_user,
            access_token=session.get('access_token')
        )
    except google.auth.exceptions.RefreshError as error:
        return redirect(url_for('gdrive_acknowledge'))


    # if not current_user.gdrive_permission_granted:
    #     return redirect(url_for('index'))
        
    if request.method == 'GET':
        return render_template('book/upload.html')

    file = request.files['file']
    try:
        metadata = extract_metadata_from_epub(file)
    except:
        flash('Not a valid epub file', 'danger')
        return redirect(url_for('upload_ebook_file'))

    book_api_data = gbooks.get_book_by_title_author(
        metadata['title'], metadata['authors'][0]
    )

    if not app.config['BYPASS_UPLOAD']:
        book_gdrive_id = gdrive.generate_file_id(credentials)
    else:
        book_gdrive_id = book_info.get('id') + secrets.token_urlsafe(20)

    if book_api_data:
        book = book_model_from_api_data(current_user.id, book_api_data)
    else:
        book = UserBook(
            user_id =   current_user.id,
            title =     metadata['title'],
            authors =   authors_from_author_list(
                metadata['authors'],
                current_user.id
            ),
            publisher = metadata.get('publisher'),
            publication_year = metadata.get('publication_year')
        )
    book.gdrive_id = book_gdrive_id
    if not app.config['BYPASS_UPLOAD']:
        gdrive.upload_file(
            credentials,
            file,
            f'{book.title} - {book.authors[0]}',
            gdrive.get_app_folder_id(credentials),
            book_gdrive_id
        )
    db.session.add(book)
    db.session.commit()

    return redirect(url_for('edit_book_details', book_id=book.gdrive_id))

@app.route('/book/<book_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_book(book_id):

    try:
        credentials = gauth.create_credentials(
            user=current_user,
            access_token=session.get('access_token')
        )
    except google.auth.exceptions.RefreshError as error:
        return redirect(url_for('gdrive_acknowledge'))

    book = UserBook.query.get_or_404({
        'user_id': current_user.id,
        'gdrive_id': book_id
    })
    
    if request.method == 'GET':
        return render_template('book/delete-confirm.html', book=book)

    gdrive_id = book.gdrive_id
    try:
        db.session.delete(book)
        db.session.commit()
    except:
        db.session.rollback()
    
    gdrive.delete_file(credentials, gdrive_id)
    # try:
    #     gdrive.delete_file(credentials, gdrive_id)
    # except:
    #     pass
    #     # TODO: Handle error

    flash('File successfully deleted', 'success')
    return redirect(url_for('index'))
