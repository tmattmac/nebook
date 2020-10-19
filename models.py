from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import array_agg
from flask_login import UserMixin
from flask_bcrypt import check_password_hash, generate_password_hash

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    username = db.Column(db.String(25), unique=True, nullable=False)

    email = db.Column(db.Text, nullable=False)

    password = db.Column(db.Text, nullable=False)

    gdrive_refresh_token = db.Column(db.Text)

    gdrive_permission_granted = db.Column(db.Boolean)

    books = db.relationship('UserBook', primaryjoin='User.id==UserBook.user_id')

    def add_book(self, book_id, gdrive_id):

        new_book = UserBook(
            user_id=self.id,
            book_id=book_id,
            gdrive_id=gdrive_id
        )
        db.session.add(new_book)
        db.session.commit()

        

    @classmethod
    def authenticate_user(cls, username, password):
        """Authenticate user with provided credentials"""

        user = cls.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.password, password):
            return False

        return user

    @classmethod
    def create_user(cls, username, email, password):
        """Create a new user and attempt to add them to database"""

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)

        try:
            db.session.commit()
            return new_user
        except IntegrityError:
            return False

class Book(db.Model):

    __tablename__ = 'books'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    gbooks_id = db.Column(db.Text, unique=True)

    title = db.Column(db.Text, nullable=False)

    subtitle = db.Column(db.Text)

    publisher = db.Column(db.Text)

    publication_year = db.Column(db.Integer)

    authors = db.relationship('Author', secondary='books_authors')


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

    gdrive_id = db.Column(db.Text, primary_key=True, unique=True)

    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

    comments = db.Column(db.Text)

    progress_percentage = db.Column(db.Float, default=0.0)

    title = db.Column(db.Text)

    publisher = db.Column(db.Text)

    publication_year = db.Column(db.Integer)

    book = db.relationship('Book',
        primaryjoin='UserBook.book_id==Book.id',
        lazy='noload')

    authors = db.relationship('Author',
        secondary='books_authors',
        primaryjoin='UserBook.book_id==BookAuthor.book_id',
        secondaryjoin='BookAuthor.author_id==Author.id')

    custom_authors = db.relationship('Author',
        secondary='custom_authors',
        primaryjoin='and_(UserBook.gdrive_id==CustomAuthor.gdrive_id, \
                            UserBook.user_id==CustomAuthor.user_id)',
        secondaryjoin='CustomAuthor.author_id==Author.id')

    def get_authors(self):
        return custom_authors or authors

class CustomAuthor(db.Model):

    __tablename__ = 'custom_authors'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    gdrive_id = db.Column(db.Text, db.ForeignKey('users_books.gdrive_id'), primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), primary_key=True)


class Tag(db.Model):

    __tablename__ = 'tags'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    tag_name = db.Column(db.Text, nullable=False)


class BookTag(db.Model):

    __tablename__ = 'books_tags'

    book_gdrive_id = db.Column(db.Text, db.ForeignKey('users_books.gdrive_id'), primary_key=True)

    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)