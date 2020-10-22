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

class Author(db.Model):

    __tablename__ = 'authors'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    name = db.Column(db.Text, nullable=False)

    books = db.relationship('UserBook',
        secondary='books_authors',
        primaryjoin='BookAuthor.author_id==Author.id',
        secondaryjoin = 'and_(UserBook.gdrive_id==BookAuthor.book_gdrive_id, \
                        UserBook.user_id == Author.user_id) ',
        back_populates='authors')

class BookAuthor(db.Model):

    __tablename__ = 'books_authors'

    book_gdrive_id = db.Column(db.Text, db.ForeignKey('users_books.gdrive_id'), primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), primary_key=True)

    is_main_author = db.Column(db.Boolean, default=False)


class UserBook(db.Model):

    __tablename__ = 'users_books'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    gdrive_id = db.Column(db.Text, primary_key=True, unique=True)

    gbooks_id = db.Column(db.Text)

    comments = db.Column(db.Text)

    progress_percentage = db.Column(db.Float, default=0.0)

    last_read = db.Column(db.DateTime)

    title = db.Column(db.Text)

    publisher = db.Column(db.Text)

    publication_year = db.Column(db.Integer)

    authors = db.relationship('Author',
        secondary='books_authors',
        primaryjoin='UserBook.gdrive_id==BookAuthor.book_gdrive_id',
        secondaryjoin = 'and_(BookAuthor.author_id==Author.id, \
                        UserBook.user_id == Author.user_id) ',
        back_populates='books')


class Tag(db.Model):

    __tablename__ = 'tags'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    tag_name = db.Column(db.Text, nullable=False)


class BookTag(db.Model):

    __tablename__ = 'books_tags'

    book_gdrive_id = db.Column(db.Text, db.ForeignKey('users_books.gdrive_id'), primary_key=True)

    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)