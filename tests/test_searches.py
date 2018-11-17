import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch, call

from fhirball.exceptions import QueryValidationError
from fhirball.db.backends.SQLAlchemy import searches as searches_sqla
from fhirball.db.backends.DjangoORM import searches as searches_django


class TestSQLAlchemy(unittest.TestCase):
    def setUp(self):
        self.NumericSearch = searches_sqla.NumericSearch
        self.NumericSearchWithQuantity = searches_sqla.NumericSearchWithQuantity
        self.MockPath = "fhirball.db.backends.SQLAlchemy.searches.NumericSearch"
        column = Mock()
        column.__lt__ = Mock()
        column.__gt__ = Mock()
        column.__le__ = Mock()
        column.__ge__ = Mock()
        column.__eq__ = Mock()
        column.__ne__ = Mock()
        self.column = column
        self.cls = SimpleNamespace(name=column)
        self.sql_query = Mock()
        self.search = self.NumericSearch("name")

    def test_numeric_search_lt(self):

        self.search(self.cls, "", "lt2", self.sql_query, "")
        self.column.__lt__.assert_called_once_with(2.0)
        self.sql_query.filter.assert_called_with(self.column.__lt__())

    def test_numeric_search_gt(self):

        self.search(self.cls, "", "gt2.35", self.sql_query, "")
        self.column.__gt__.assert_called_once_with(2.35)
        self.sql_query.filter.assert_called_with(self.column.__gt__())

    def test_numeric_search_le(self):

        self.search(self.cls, "", "le235", self.sql_query, "")
        self.column.__le__.assert_called_with(235)
        self.sql_query.filter.assert_called_with(self.column.__le__())

    def test_numeric_search_ge(self):

        self.search(self.cls, "", "ge0.0005", self.sql_query, "")
        self.column.__ge__.assert_called_once_with(0.0005)
        self.sql_query.filter.assert_called_with(self.column.__ge__())

    def test_numeric_search_eq(self):

        self.search(self.cls, "", "eq123", self.sql_query, "")
        self.column.__eq__.assert_called_with(123)
        self.sql_query.filter.assert_called_with(self.column.__eq__())

    def test_numeric_search_ne(self):

        self.search(self.cls, "", "ne321", self.sql_query, "")
        self.column.__ne__.assert_called_with(321)
        self.sql_query.filter.assert_called_with(self.column.__ne__())

    def test_numeric_search_ap(self):

        self.search(self.cls, "", "ap1000", self.sql_query, "")
        self.column.__ge__.assert_called_with(900)
        self.column.__le__.assert_called_with(1100)
        self.sql_query.filter.assert_called_with(self.column.__ge__())
        self.sql_query.filter().filter.assert_called_with(self.column.__le__())

    def test_numeric_search(self):

        self.search(self.cls, "", "1111", self.sql_query, "")
        self.column.__eq__.assert_called_with(1111)
        self.sql_query.filter.assert_called_with(self.column.__eq__())
        QVD = QueryValidationError
        self.assertRaises(QVD, self.search, self.cls, "", "asde", self.sql_query, "")
        self.assertRaises(QVD, self.search, self.cls, "", "nea321", self.sql_query, "")
        self.assertRaises(QVD, self.search, self.cls, "", "nea32 1", self.sql_query, "")

    def test_numeric_search_with_quantity(self):
        with patch(self.MockPath) as mocked:
            cv = Mock()
            aq = Mock()
            search = self.NumericSearchWithQuantity("value", convert_value=cv)
            search("a", "a", "eq123|mg", "f", "query")
            cv.assert_called_with("eq123", "mg")
            aq.assert_not_called()
            mocked.assert_called_with("value")
            mocked.assert_has_calls([call().search("a", "a", cv(), "f", "query")])

            cv = Mock()
            aq = Mock()
            search = self.NumericSearchWithQuantity("value", alter_query=aq)
            search("a", "a", "eq123|mg", "f", "query")
            cv.assert_not_called()
            aq.assert_called_with("query", "eq123", "mg")

            cv = Mock()
            aq = Mock()
            search = self.NumericSearchWithQuantity(
                "value", convert_value=cv, alter_query=aq
            )
            search("a", "a", "eq123|http://unitsofmeasure.org|mg", "f", "query")
            cv.assert_called_with("eq123", "http://unitsofmeasure.org|mg")
            aq.assert_called_with("query", cv(), "http://unitsofmeasure.org|mg")


class TestDjangoORM(TestSQLAlchemy):
    def setUp(self):
        self.NumericSearch = searches_django.NumericSearch
        self.NumericSearchWithQuantity = searches_django.NumericSearchWithQuantity
        self.MockPath = "fhirball.db.backends.DjangoORM.searches.NumericSearch"
        column = Mock()
        self.column = column
        self.cls = SimpleNamespace(name=column)
        self.sql_query = Mock()
        self.search = self.NumericSearch("name")

    def test_numeric_search_lt(self):
        self.search(self.cls, "", "lt2", self.sql_query, "")
        self.sql_query.filter.assert_called_with(name__lt=2.0)

    def test_numeric_search_gt(self):
        self.search(self.cls, "", "gt2.35", self.sql_query, "")
        self.sql_query.filter.assert_called_with(name__gt=2.35)

    def test_numeric_search_le(self):
        self.search(self.cls, "", "le235", self.sql_query, "")
        self.sql_query.filter.assert_called_with(name__lte=235)

    def test_numeric_search_ge(self):
        self.search(self.cls, "", "ge0.0005", self.sql_query, "")
        self.sql_query.filter.assert_called_with(name__gte=0.0005)

    def test_numeric_search_eq(self):
        self.search(self.cls, "", "eq123", self.sql_query, "")
        self.sql_query.filter.assert_called_with(name=123)

    def test_numeric_search_ne(self):
        self.search(self.cls, "", "ne321", self.sql_query, "")
        self.sql_query.filter.assert_called_with(name__ne=321)

    def test_numeric_search_ap(self):
        self.search(self.cls, "", "ap1000", self.sql_query, "")
        self.sql_query.filter.assert_called_with(name__gte=900.0)
        self.sql_query.filter().filter.assert_any_call(name__lte=1100.0)

    def test_numeric_search(self):
        self.search(self.cls, "", "1111", self.sql_query, "")
        self.sql_query.filter.assert_called_with(name=1111)

        QVE = QueryValidationError
        self.assertRaises(QVE, self.search, self.cls, "", "asde", self.sql_query, "")
        self.assertRaises(QVE, self.search, self.cls, "", "nea321", self.sql_query, "")
        self.assertRaises(QVE, self.search, self.cls, "", "nea32 1", self.sql_query, "")
