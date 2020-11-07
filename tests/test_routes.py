from unittest import TestCase
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///book_project_test'
app.config['BYPASS_UPLOAD'] = True
