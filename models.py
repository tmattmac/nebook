from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    username = db.Column(db.String(25), unique=True, nullable=False)

    password = db.Column(db.Text, nullable=False)

    gdrive_refresh_token = db.Column(db.Text)

    gdrive_permission_granted = db.Column(db.Boolean)

    # TODO: Add Flask authentication code


class Book(db.Model):

    __tablename__ = 'books'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    gbooks_id = db.Column(db.Text, unique=True)

    title = db.Column(db.Text, nullable=False)

    subtitle = db.Column(db.Text)

    publisher = db.Column(db.Text)

    publication_year = db.Column(db.Integer)

    authors = db.relationship('authors', secondary='books_authors')


class Author(db.Model):

    __tablename__ = 'authors'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    name = db.Column(db.Text, unique=True, nullable=False)


class BookAuthor(db.Model):

    __tablename__ = 'books_authors'

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), primary_key=True)

    is_main_author = db.Column(db.Boolean, default=False)


class UserBook(db.Model):

    __tablename__ = 'users_books'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    gdrive_id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

    comments = db.Column(db.Text)

    progress_percentage = db.Column(db.Float, default=0.0)

    title = db.Column(db.Text)

    publisher = db.Column(db.Text)

    publication_year = db.Column(db.Integer)


class CustomAuthor(db.Model):

    __tablename__ = 'custom_authors'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    book_id = db.Column(db.Integer, db.ForeignKey('users.book_id'), primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), primary_key=True)


class Tag(db.Model):

    __tablename__ = 'tags'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    tag_name = db.Column(db.Text, nullable=False, primary_key=True)


class UserBookTag(db.Model):

    __tablename__ 'users_books_tags'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    book_gdrive_id = db.Column(db.Text, db.ForeignKey('users_books.gdrive_id'), primary_key=True)

    tag_name = db.Column(db.Text, db.ForeignKey('tags.tag_name'), primary_key=True)