from django.core.paginator import Paginator
from fhirbug.models.pagination import Page


def paginate(query, page, page_size):
    '''
    Implement pagination for Django ORM.
    '''
    if page <= 0:
        raise AttributeError('page needs to be >= 1')
    if page_size <= 0:
        raise AttributeError('page_size needs to be >= 1')
    items = query.all()
    paginator = Paginator(items, page_size)
    items = paginator.get_page(page)
    total = query.count()
    return Page(items, page, page_size, total)
