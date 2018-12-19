from fhirbug.models.pagination import Page


def paginate(query, page, page_size):
    '''
    Implement pagination for SQLAlchemy.
    '''
    if page <= 0:
        raise AttributeError('page needs to be >= 1')
    if page_size <= 0:
        raise AttributeError('page_size needs to be >= 1')
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    total = query.order_by(None).count()
    return Page(items, page, page_size, total)
