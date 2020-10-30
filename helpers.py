from sqlalchemy import or_, desc, func, nullslast
from models import *

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
    SORT_FIELDS = ['title', 'publisher', 'publication_year', 'last_read', 'author']

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
        author_name = Author.query.get(author).name
        if author_name:
            search_meta['author'] = author_name
            query = query.filter(Author.id == author)
    if tag:
        tag_name = Tag.query.get(tag).tag_name
        if tag_name:
            search_meta['tag'] = tag_name
            query = query.filter(Tag.id == tag)
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
        'authors':          [],
        'tags':             []
    }
    for author_name in form.authors.data:
        author = get_or_create(Author, name=author_name, user_id=user.id)
        book['authors'].append(author)
    for tag_name in form.tags.data:
        tag = get_or_create(Tag, tag_name=tag_name, user_id=user.id)
        book['tags'].append(tag)

    for k, v in book.items():
        setattr(book_instance, k, v)

    db.session.add(book_instance)
    db.session.commit()