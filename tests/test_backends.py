import unittest
# from datetime import date, datetime
# from types import SimpleNamespace
from unittest.mock import Mock, patch, MagicMock

# from fhirbug.exceptions import QueryValidationError
from fhirbug.db.backends.SQLAlchemy.pagination import paginate as paginate_sqla
from fhirbug.db.backends.DjangoORM.pagination import paginate as paginate_django
from fhirbug.db.backends.pymodm.pagination import paginate as paginate_pymodm


class TestSQLAlchemyPaginate(unittest.TestCase):
    # def setUp(self):
    def test_value_checks(self):
        with self.assertRaises(AttributeError) as e:
            paginate_sqla('query', -1, 1)
        self.assertEqual(e.exception.args[0], "page needs to be >= 1")
        with self.assertRaises(AttributeError) as e:
            paginate_sqla('query', 1, -1)
        self.assertEqual(e.exception.args[0], "page_size needs to be >= 1")

    @patch('fhirbug.db.backends.SQLAlchemy.pagination.Page')
    def test_paginate(self, PageMock):
        query = Mock()
        ret = paginate_sqla(query, 4, 10)
        query.limit.assert_called_with(10)
        query.limit().offset.assert_called_with((4-1)*10)
        query.limit().offset().all.assert_called()

        query.order_by.assert_called_with(None)
        query.order_by().count.assert_called()
        PageMock.assert_called_with(query.limit().offset().all(), 4, 10, query.order_by().count())
        self.assertEqual(ret, PageMock())


class TestDjangoORMPaginate(unittest.TestCase):
    # def setUp(self):
    def test_value_checks(self):
        with self.assertRaises(AttributeError) as e:
            paginate_django('query', -1, 1)
        self.assertEqual(e.exception.args[0], "page needs to be >= 1")
        with self.assertRaises(AttributeError) as e:
            paginate_django('query', 1, -1)
        self.assertEqual(e.exception.args[0], "page_size needs to be >= 1")

    @patch('fhirbug.db.backends.DjangoORM.pagination.Paginator')
    @patch('fhirbug.db.backends.DjangoORM.pagination.Page')
    def test_paginate(self, PageMock, PaginatorMock):
        query = Mock()
        ret = paginate_django(query, 4, 10)
        query.all.assert_called()
        PaginatorMock.assert_called_with(query.all(), 10)
        PaginatorMock().get_page.assert_called_with(4)
        query.count.assert_called()

        PageMock.assert_called_with(PaginatorMock().get_page(), 4, 10, query.count())
        self.assertEqual(ret, PageMock())


class TestPyMODMPaginate(unittest.TestCase):
    # def setUp(self):
    def test_value_checks(self):
        with self.assertRaises(AttributeError) as e:
            paginate_pymodm('query', -1, 1)
        self.assertEqual(e.exception.args[0], "page needs to be >= 1")
        with self.assertRaises(AttributeError) as e:
            paginate_pymodm('query', 1, -1)
        self.assertEqual(e.exception.args[0], "page_size needs to be >= 1")

    @patch('fhirbug.db.backends.pymodm.pagination.Page')
    def test_paginate(self, PageMock):
        query = MagicMock()
        ret = paginate_pymodm(query, 4, 10)

        query.limit.assert_called_with(10)
        query.limit().skip.assert_called_with((4-1)*10)
        query.limit().skip().all.assert_called()
        query.count.assert_called()

        PageMock.assert_called_with(list(query.limit().skip().all()), 4, 10, query.count())
        self.assertEqual(ret, PageMock())
