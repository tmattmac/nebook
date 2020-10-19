from lib import epubtag
from models import *
import gdrive
import gbooks

def parse_year(date_string):
    try:
        return [part for part in date_string.split('-') if len(part) == 4][0]
    except:
        return None

def book_model_from_api_data(api_data):

    # Return book as-is if it exists
    book = Book.query.filter_by(gbooks_id=api_data['id']).first()
    if book:
        return book

    metadata = api_data['volumeInfo']
    book = Book(
        gbooks_id=api_data['id'],
        title=metadata.get('title'),
        subtitle=metadata.get('subtitle'),
        publisher=metadata.get('publisher'),
        publication_year=parse_year(metadata.get('publishedDate'))
    )

    # Create any authors not already in database
    author_names = metadata.get('authors', [])
    authors = Author.query.filter(Author.name.in_(author_names)).all()
    author_names = set(author_names) - set([author.name for author in authors])
    for name in author_names:
        authors.append(Author(name=name))

    book.authors = authors

    return book

