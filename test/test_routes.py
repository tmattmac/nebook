from unittest import TestCase
from app import app
from models import db, User, UserBook, Author, connect_db
from flask import url_for
import io
import os

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///book_project_test'
app.config['BYPASS_UPLOAD'] = True
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

connect_db(app)
db.drop_all()
db.create_all()

TEST_USER = {'username': 'test', 'password': 'password'}
TEST_USER_INSTANCE = User.create_user(
    TEST_USER['username'],
    'a@b.com',
    TEST_USER['password']
)
TEST_AUTHOR = Author(name='Test Author')
TEST_BOOK_1 = {
    'gdrive_id': 'test_book_1',
    'title': 'Test Book 1',
    'authors': [TEST_AUTHOR]
}
TEST_BOOK_2 = {
    'gdrive_id': 'test_book_2',
    'title': 'Test Book 2',
    'authors': [TEST_AUTHOR]
}

# Get absolute path for test files
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

class UserRoutesTestCase(TestCase):

    def setUp(self):
        db.session.add(TEST_USER_INSTANCE)
        TEST_USER_INSTANCE.books = [
            UserBook(**TEST_BOOK_1),
            UserBook(**TEST_BOOK_2)
        ]
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        db.session.add(TEST_USER_INSTANCE)
        TEST_USER_INSTANCE.books = []
        db.session.commit()

    def test_empty_index_page(self):
        with app.test_client() as client:

            # Get rid of books
            db.session.add(TEST_USER_INSTANCE)
            TEST_USER_INSTANCE.books = []
            db.session.commit()

            res = client.post('/login', data=TEST_USER)

            res = client.get('/', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('no books', html)

    def test_index_page_with_books(self):
        with app.test_client() as client:
            res = client.post('/login', data=TEST_USER)

            res = client.get('/', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Test Book 1', html)
            self.assertIn('Test Book 2', html)

    def test_upload_page(self):
        with app.test_client() as client:
            res = client.post('/login', data=TEST_USER)

            res = client.get(url_for('upload_ebook_file'), follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2>Upload', html)

    def test_upload_book(self):
        with app.test_client() as client:
            res = client.post('/login', data=TEST_USER)

            filepath = os.path.join(THIS_FOLDER, 'cyrano.epub')
            file = open(filepath, 'rb', buffering=0)
            data = {
                'file': (file, 'cyrano.epub')
            }
            
            res = client.post(
                url_for('upload_ebook_file'),
                follow_redirects=True,
                data=data,
                content_type='multipart/form-data'
            )

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Edit details', html)
            self.assertIn('Cyrano de', html)

    def test_upload_invalid_book(self):
        with app.test_client() as client:
            res = client.post('/login', data=TEST_USER)

            filepath = os.path.join(THIS_FOLDER, 'test.jpg')
            file = open(filepath, 'rb', buffering=0)
            data = {
                'file': (file, 'cyrano.epub')
            }
            
            res = client.post(
                url_for('upload_ebook_file'),
                follow_redirects=True,
                data=data,
                content_type='multipart/form-data'
            )

            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2>Upload', html)
            self.assertIn('valid epub file', html)

    def test_edit_book_page(self):
        with app.test_client() as client:
            res = client.post('/login', data=TEST_USER)

            res = client.get(
                url_for('edit_book_details', book_id=TEST_BOOK_1['gdrive_id']),
                follow_redirects=True
            )
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Edit details', html)
            self.assertIn('Test Book 1', html)

            # Request with invalid parameter
            res = client.get(
                url_for('edit_book_details', book_id='invalid_id'),
                follow_redirects=True
            )

            self.assertEqual(res.status_code, 404)

    def test_edit_book_form(self):
        with app.test_client() as client:
            res = client.post('/login', data=TEST_USER)

            # Valid form data
            form_data = {
                'title': 'Different Test Book',
                'authors': 'Test Author 1, Test Author 2',
                'tags': 'tag1, tag2'
            }

            res = client.post(
                url_for('edit_book_details', book_id=TEST_BOOK_1['gdrive_id']),
                follow_redirects=True,
                data=form_data
            )
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Details for', html)
            self.assertIn(form_data['title'], html)
            self.assertIn('Test Author 1', html)
            self.assertIn('Test Author 2', html)
            self.assertIn('tag1', html)
            self.assertIn('tag2', html)

            # Invalid form data
            form_data['title'] = ''

            res = client.post(
                url_for('edit_book_details', book_id=TEST_BOOK_1['gdrive_id']),
                follow_redirects=True,
                data=form_data
            )
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn('Edit details', html)
            self.assertIn('invalid-feedback', html)

    def test_delete_book(self):
        with app.test_client() as client:
            res = client.post('/login', data=TEST_USER)

            res = client.get(
                url_for('delete_book', book_id=TEST_BOOK_1['gdrive_id']),
                follow_redirects=True
            )
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Are you sure you want to delete', html)
            self.assertIn(TEST_BOOK_1["title"], html)
            
            # Confirm deletion
            res = client.post(
                url_for('delete_book', book_id=TEST_BOOK_1['gdrive_id']),
                follow_redirects=True
            )
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('successfully deleted', html)
            self.assertNotIn(TEST_BOOK_1['title'], html)

            # Invalid book
            res = client.get(
                url_for('delete_book', book_id='invalid_id'),
                follow_redirects=True
            )

            self.assertEqual(res.status_code, 404)
