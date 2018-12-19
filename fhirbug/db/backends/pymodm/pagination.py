from fhirbug.models.pagination import Page


def paginate(query, page, page_size):
    """
    Implement pagination for Django ORM.
    """
    if page <= 0:
        raise AttributeError("page needs to be >= 1")
    if page_size <= 0:
        raise AttributeError("page_size needs to be >= 1")
    items = query.limit(page_size).skip((page - 1) * page_size).all()
    total = query.count()
    return Page(list(items), page, page_size, total)
