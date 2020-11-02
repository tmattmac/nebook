from sqlalchemy import or_, and_, desc, func, nullslast, text
from models import *
from lib.epubtag import EpubBook
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

def build_query(user, **kwargs):
    """
    Build a query on books based on provided query parameters
    q       search query
    pg      page of results (default: 1)
    per_pg  number of results to show per page (default: 20)
    author  filter by author with specified id
    sort    name of column to sort by (default: last_read)
    order   asc or desc (default: )
    """
    SORT_FIELDS = {
        'title': UserBook.title,
        'publisher': UserBook.publisher,
        'publication_year': UserBook.publication_year,
        'last_read': UserBook.last_read,
        'author': Author.name
    }

    # TODO: Get items per page from user preferences
    pg = kwargs.get('pg', 1) - 1
    per_pg = kwargs.get('per_pg', 20)
    sort = kwargs.get('sort')
    order = kwargs.get('order')
    author = kwargs.get('author')
    tag = kwargs.get('tag')
    q = kwargs.get('q')
    publisher = kwargs.get('publisher')
    year = kwargs.get('year')

    search_meta = {}

    query = db.session.query(UserBook)\
        .filter(UserBook.user_id == user.id)\
        .outerjoin(UserBook.authors)\
        .outerjoin(UserBook.tags)

    if author:
        # TODO: Try-except block
        query = query.filter(Author.id.in_(author))
        if len(author) == 1:
            search_meta['author'] = Author.query.get(author[0]).name
        else:
            search_meta['author'] = '(multiple authors)'
            
    if tag:
        query = query.filter(Tag.id.in_(tag))
        if len(tag) == 1:
            search_meta['tag'] = Tag.query.get(tag[0]).tag_name
        else:
            search_meta['tag'] = '(multiple tags)'

    if publisher:
        search_meta['publisher'] = publisher
        query = query.filter(UserBook.publisher.ilike(f'%{publisher}%'))

    if year:
        search_meta['year'] = year
        query = query.filter(UserBook.publication_year == year)

    if q:
        search_meta['q'] = q
        q = f'%{q}%'
        query = query.filter(or_(
            UserBook.title.ilike(q),
            UserBook.publisher.ilike(q),
            Tag.tag_name.ilike(q),
            Author.name.ilike(q)
        ))

    if not sort or sort not in SORT_FIELDS:
        sort = 'last_read'
        order = 'desc'
    elif sort == 'author':
        sort = Author.name

    if sort == 'last_read':
        order = order or 'desc'

    sort = SORT_FIELDS[sort]

    if order == 'desc':
        query = query.order_by(desc(sort).nullslast())
    else:
        query = query.order_by(nullslast(sort))

    count = query.count()
    search_meta['count'] = count

    query = query\
            .limit(per_pg)\
            .offset(pg * per_pg)

    return query.all(), search_meta


def update_book_with_form_data(book_instance, form):
    book = {
        'title':            form.title.data,
        'publisher':        form.publisher.data,
        'publication_year': form.publication_year.data,
        'comments':         form.comments.data,
        'cover_image':      form.cover_image.data,
        'authors':          [],
        'tags':             []
    }
    for author_name in form.authors.data:
        author = get_or_create(Author, name=author_name, user_id=book_instance.user_id)
        book['authors'].append(author)
    for tag_name in form.tags.data:
        tag = get_or_create(Tag, tag_name=tag_name, user_id=book_instance.user_id)
        book['tags'].append(tag)

    for k, v in book.items():
        setattr(book_instance, k, v)

    db.session.add(book_instance)
    db.session.commit()


def parse_year(date_string):
    '''Pull the year out of a formatted date string'''
    try:
        return [part for part in date_string.split('-') if len(part) == 4][0]
    except:
        return None


def remove_page_curl(url):
    '''Remove edge=curl parameter from Google Books API cover image'''
    parsed_url = list(urlparse(url))
    query = parse_qs(parsed_url[4])
    query.pop('edge')
    parsed_url[4] = urlencode(query, doseq=True)
    new_url = urlunparse(parsed_url)
    return new_url

def book_model_from_api_data(user_id, api_data):

    metadata = api_data['volumeInfo']

    # Get thumbnails if they exist, remove page curl from resulting url
    thumbnails = metadata.get('imageLinks')
    cover_image = thumbnails.get('thumbnail') if thumbnails else None
    cover_image = remove_page_curl(cover_image) if cover_image else None

    book = UserBook(
        user_id=user_id,
        gbooks_id=api_data['id'],
        title=metadata.get('title'),
        publisher=metadata.get('publisher'),
        publication_year=parse_year(metadata.get('publishedDate')),
        cover_image=cover_image
    )

    # Create list of authors and add to created book instance
    author_names = metadata.get('authors', [])
    book.authors = authors_from_author_list(author_names, user_id)

    return book

def authors_from_author_list(author_names, user_id):
    # Create any authors not already in database
    authors = Author.query.filter(
        and_(
            Author.name.in_(author_names),
            Author.user_id == user_id
        )
    ).all()
    author_names = set(author_names) - set([author.name for author in authors])
    for name in author_names:
        authors.append(Author(name=name, user_id=user_id))

    return authors

def extract_metadata_from_epub(file_handle):
    metadata = {}
    epub = EpubBook(file_handle)
    metadata['title'] = epub.get_title()
    metadata['authors'] = epub.get_authors()
    publisher, _, _ = epub.get_matches('dc:publisher')
    date, _, _ = epub.get_matches('dc:date')

    if publisher:
        metadata['publisher'] = publisher[0]
    if date:
        metadata['publication_year'] = parse_year(date[0])

    return metadata

def get_tags(user_id):
    tags = db.session.query(Tag)\
        .filter(Tag.user_id==user_id)\
        .join(Tag.books)\
        .order_by(Tag.tag_name)\
        .all()

    return tags

def get_authors(user_id):
    authors = db.session.query(Author)\
        .filter(Author.user_id==user_id)\
        .join(Author.books)\
        .order_by(Author.name)\
        .all()

    return authors