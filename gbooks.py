from googleapiclient.discovery import build
from googleapiclient import errors

GDRIVE_APP_FOLDER = 'UBP Ebooks'
API_NAME = 'books'
API_VERSION = 'v1'

books = build(API_NAME, API_VERSION, credentials={})

def get_book_by_title_author(title, author):
    
    results = books.volumes().list(
        q=f"intitle:'{title}' inauthor:'{author}'"
    ).execute()

    if results['totalItems'] > 0:
        return results['items'][0]