import math


class Page:
    '''
    Base class for holding paginated results along with pagination metadata.

    >>> p = Page([1]*20, 2, 20, 100)
    >>> p.has_next
    True
    >>> p.has_previous
    True
    >>> p.next_page
    3
    >>> p.previous_page
    1
    >>> p.pages
    5


    >>> p = Page([1]*20, 1, 20, 100)
    >>> p.has_previous
    False
    >>> p.previous_page
    >>> p.pages
    5

    >>> p = Page([1]*20, 5, 20, 100)
    >>> p.has_next
    False
    >>> p.has_previous
    True
    >>> p.next_page
    >>> p.previous_page
    4
    >>> p.pages
    5
    '''

    def __init__(self, items, page, page_size, total):
        self.items = items
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 1
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = (page - 1) * page_size
        self.has_next = previous_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(math.ceil(total / float(page_size)))
