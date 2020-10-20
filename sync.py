from lib import epubtag
from models import *
import gdrive
import gbooks

def parse_year(date_string):
    try:
        return [part for part in date_string.split('-') if len(part) == 4][0]
    except:
        return None

def book_model_from_api_data(user_id, api_data):

    metadata = api_data['volumeInfo']
    book = UserBook(
        user_id=user_id,
        gbooks_id=api_data['id'],
        title=metadata.get('title'),
        publisher=metadata.get('publisher'),
        publication_year=parse_year(metadata.get('publishedDate'))
    )

    # Create any authors not already in database
    author_names = metadata.get('authors', [])
    authors = Author.query.filter(
        and_(
            Author.name.in_(author_names),
            Author.user_id == user_id
        )
    ).all()
    author_names = set(author_names) - set([author.name for author in authors])
    for name in author_names:
        authors.append(Author(name=name, user_id=user_id))

    book.authors = authors

    return book

