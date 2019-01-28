import unittest
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch, call

from fhirbug.exceptions import QueryValidationError
from fhirbug.db.backends.SQLAlchemy import searches as searches_sqla
from fhirbug.db.backends.DjangoORM import searches as searches_django
from fhirbug.db.backends.pymodm import searches as searches_pymodm


###
# SQLAlchemy
###
class TestSQLAlchemyNumeric(unittest.TestCase):
    def setUp(self):
        self.NumericSearch = searches_sqla.NumericSearch
        self.NumericSearchWithQuantity = searches_sqla.NumericSearchWithQuantity
        self.MockPath = "fhirbug.db.backends.SQLAlchemy.searches.NumericSearch"
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


class TestSQLAlchemyString(unittest.TestCase):
    def setUp(self):
        self.StringSearch = searches_sqla.StringSearch
        self.MockPath = "fhirbug.db.backends.SQLAlchemy.searches.or_"
        column = Mock()
        column.__eq__ = Mock()
        self.column = column
        self.cls = SimpleNamespace(name=column)
        self.sql_query = Mock()
        self.search = self.StringSearch("name")

    def test_search_no_args(self):
        """
        Stringsearch should raise TypeError if it is initialized without a column name
        """
        self.assertRaises(TypeError, self.StringSearch)

    def test_search_simple(self):
        """
        With simple arguments it shoud do a `startswith` query
        """
        with patch(self.MockPath) as or_:
            self.search(self.cls, "name", "bob", self.sql_query, None)
            self.sql_query.filter.assert_called_with(or_())
            args = next(or_.call_args_list[0][0][0])
            self.column.startswith.assert_called_with("bob")
            self.assertEquals(args, self.column.startswith())

    def test_search_contains(self):
        """
        With the `contains` modifier it should do a `contains` query
        """
        with patch(self.MockPath) as or_:
            self.search(self.cls, "name:contains", "bob", self.sql_query, None)
            self.sql_query.filter.assert_called_with(or_())
            args = next(or_.call_args_list[0][0][0])
            self.column.contains.assert_called_with("bob")
            self.assertEquals(args, self.column.contains())

    def test_search_exact(self):
        """
        With the `exact` modifier it should do an equality query
        """
        with patch(self.MockPath) as or_:
            self.search(self.cls, "name:exact", "guy", self.sql_query, None)
            self.sql_query.filter.assert_called_with(or_())
            args = next(or_.call_args_list[0][0][0])
            self.column.__eq__.assert_called_with("guy")
            self.assertEquals(args, self.column.__eq__())

    def test_search_multiple_columns(self):
        """
        Multiple column names can be passed to the search constructor which will be
        joined together with or in the resulting query.
        """
        search = self.StringSearch("first_name", "last_name")
        column1 = Mock()
        column2 = Mock()
        cls = SimpleNamespace(first_name=column1, last_name=column2)
        with patch(self.MockPath) as or_:
            search(cls, "name", "John", self.sql_query, None)
            self.sql_query.filter.assert_called_with(or_())
            args = list(or_.call_args_list[0][0][0])
            column1.startswith.assert_called_with("John")
            column2.startswith.assert_called_with("John")
            self.assertEquals(args, [column1.startswith(), column2.startswith()])


class TestSQLAlchemyDate(unittest.TestCase):
    def setUp(self):
        self.DateSearch = searches_sqla.DateSearch
        #     self.MockPath = "fhirbug.db.backends.SQLAlchemy.searches.or_"
        column = Mock()
        column.__eq__ = Mock()
        column.__lt__ = Mock()
        column.__gt__ = Mock()
        column.__le__ = Mock()
        column.__ge__ = Mock()
        column.__ne__ = Mock()
        self.column = column
        self.cls = SimpleNamespace(name=column)
        self.sql_query = Mock()
        self.search = self.DateSearch("name")

    def test_transform_date(self):
        self.assertEqual(searches_sqla.transform_date("xx2013-01-01"), date(2013, 1, 1))
        self.assertEqual(
            searches_sqla.transform_date("xx2013-01-01T12:33"),
            datetime(2013, 1, 1, 12, 33, 0),
        )
        self.assertEqual(
            searches_sqla.transform_date("2014-02-03", trim=False), date(2014, 2, 3)
        )
        with self.assertRaises(QueryValidationError):
            searches_sqla.transform_date("invalid")

    def test_search_lt(self):
        self.search(self.cls, "", "lt2017-01-01", self.sql_query, "")
        self.column.__lt__.assert_called_with(date(2017, 1, 1))
        self.sql_query.filter.assert_called_with(self.column.__lt__())

    def test_search_gt(self):
        self.search(self.cls, "", "gt2018-01-01", self.sql_query, "")
        self.column.__gt__.assert_called_with(date(2018, 1, 1))
        self.sql_query.filter.assert_called_with(self.column.__gt__())

    def test_search_le(self):
        self.search(self.cls, "", "le2018-02-02", self.sql_query, "")
        self.column.__le__.assert_called_with(date(2018, 2, 2))
        self.sql_query.filter.assert_called_with(self.column.__le__())

    def test_search_ge(self):
        self.search(self.cls, "", "ge2018-03-01", self.sql_query, "")
        self.column.__ge__.assert_called_with(date(2018, 3, 1))
        self.sql_query.filter.assert_called_with(self.column.__ge__())

    def test_search_eq(self):
        self.search(self.cls, "", "eq1918-03-01", self.sql_query, "")
        self.column.__eq__.assert_called_with(date(1918, 3, 1))
        self.sql_query.filter.assert_called_with(self.column.__eq__())

    def test_search_ne(self):
        self.search(self.cls, "", "ne1928-03-02", self.sql_query, "")
        self.column.__ne__.assert_called_with(date(1928, 3, 2))
        self.sql_query.filter.assert_called_with(self.column.__ne__())

    def test_search_ap(self):
        self.search(self.cls, "", "ap1928-03-05", self.sql_query, "")
        self.column.__ge__.assert_called_with(date(1928, 2, 4))
        self.column.__le__.assert_called_with(date(1928, 4, 4))

        self.sql_query.filter.assert_called_with(self.column.__ge__())
        self.sql_query.filter().filter.assert_called_with(self.column.__le__())

    def test_searche(self):
        self.search(self.cls, "", "1928-03-02", self.sql_query, "")
        self.column.__eq__.assert_called_with(date(1928, 3, 2))
        self.sql_query.filter.assert_called_with(self.column.__eq__())


###
# Django
###
class TestDjangoORMNumeric(TestSQLAlchemyNumeric):
    def setUp(self):
        self.NumericSearch = searches_django.NumericSearch
        self.NumericSearchWithQuantity = searches_django.NumericSearchWithQuantity
        self.MockPath = "fhirbug.db.backends.DjangoORM.searches.NumericSearch"
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


class TestDjangoORMDate(unittest.TestCase):
    def setUp(self):
        self.DateSearch = searches_django.DateSearch
        column = Mock()
        self.column = column
        self.cls = SimpleNamespace(name=column)
        self.sql_query = Mock()
        self.search = self.DateSearch("date")

    def test_transform_date(self):
        self.assertEqual(
            searches_django.transform_date("xx2013-01-01"), date(2013, 1, 1)
        )
        self.assertEqual(
            searches_django.transform_date("xx2013-01-01T12:33"),
            datetime(2013, 1, 1, 12, 33, 0),
        )
        self.assertEqual(
            searches_django.transform_date("2014-02-03", trim=False), date(2014, 2, 3)
        )
        with self.assertRaises(QueryValidationError):
            searches_sqla.transform_date("invalid")

    def test_date_search_lt(self):
        self.search(self.cls, "", "lt2019-03-04", self.sql_query, "")
        self.sql_query.filter.assert_called_with(date__lt=date(2019, 3, 4))

    def test_date_search_gt(self):
        self.search(self.cls, "", "gt2019-03-04T12:34", self.sql_query, "")
        self.sql_query.filter.assert_called_with(
            date__gt=datetime(2019, 3, 4, 12, 34, 0)
        )

    def test_date_search_le(self):
        self.search(self.cls, "", "le1980-02-06", self.sql_query, "")
        self.sql_query.filter.assert_called_with(date__lte=date(1980, 2, 6))

    def test_date_search_ge(self):
        self.search(self.cls, "", "ge1980", self.sql_query, "")
        self.sql_query.filter.assert_called_with(date__gte=date(1980, 1, 1))

    def test_date_search_eq(self):
        self.search(self.cls, "", "eq1999-12", self.sql_query, "")
        self.sql_query.filter.assert_called_with(date=date(1999, 12, 1))

    @patch("fhirbug.db.backends.DjangoORM.searches.Q")
    def test_date_search_ne(self, QMock):
        self.search(self.cls, "", "ne1980-01-01", self.sql_query, "")
        self.sql_query.filter.assert_called_with(~QMock())

    def test_date_search_ap(self):
        self.search(self.cls, "", "ap1970-02-05", self.sql_query, "")
        self.sql_query.filter.assert_called_with(date__gte=date(1970, 1, 6))
        self.sql_query.filter().filter.assert_any_call(date__lte=date(1970, 3, 7))

    def test_date_search(self):
        self.search(self.cls, "", "1970-02-05T14:45:32", self.sql_query, "")
        self.sql_query.filter.assert_called_with(date=datetime(1970, 2, 5, 14, 45, 32))

        QVE = QueryValidationError
        self.assertRaises(QVE, self.search, self.cls, "", "asde", self.sql_query, "")
        self.assertRaises(QVE, self.search, self.cls, "", "nea321", self.sql_query, "")
        self.assertRaises(QVE, self.search, self.cls, "", "nea32 1", self.sql_query, "")


@patch("fhirbug.db.backends.DjangoORM.searches.Q")
class TestDjangoORMString(unittest.TestCase):
    def setUp(self):
        self.StringSearch = searches_django.StringSearch
        column = Mock()
        self.column = column
        self.cls = SimpleNamespace(name=column)
        self.sql_query = Mock()
        self.search = self.StringSearch("name")
        self.search_with_2 = self.StringSearch("name", "lastname")

    def test_search_no_args(self, Q):
        """
        Stringsearch should raise TypeError if it is initialized without a column name
        """
        self.assertRaises(TypeError, self.StringSearch)

    def test_search_simple(self, Q):
        """
        With simple arguments it shoud do a `startswith` query
        """
        self.search(self.cls, "name", "bob", self.sql_query, None)
        Q.assert_called_with(name__startswith="bob")
        self.sql_query.filter.assert_called_with(Q())

        Q.reset_mock()
        self.search_with_2(self.cls, "name", "bobb", self.sql_query, None)
        Q.assert_has_calls(
            [
                call(name__startswith="bobb"),
                call(lastname__startswith="bobb"),
                call().__ior__(Q()),
            ]
        )
        self.sql_query.filter.assert_called_with(Q().__ior__())

    def test_search_contains(self, Q):
        """
        With simple arguments it shoud do a `contains` query
        """
        self.search(self.cls, "name:contains", "John", self.sql_query, None)
        Q.assert_called_with(name__contains="John")
        self.sql_query.filter.assert_called_with(Q())

        Q.reset_mock()
        self.search_with_2(self.cls, "name:contains", "Jack", self.sql_query, None)
        Q.assert_has_calls(
            [
                call(name__contains="Jack"),
                call(lastname__contains="Jack"),
                call().__ior__(Q()),
            ]
        )
        self.sql_query.filter.assert_called_with(Q().__ior__())

    def test_search_exact(self, Q):
        """
        With simple arguments it shoud do an exact query
        """
        self.search(self.cls, "firstname:exact", "Mary", self.sql_query, None)
        Q.assert_called_with(name="Mary")
        self.sql_query.filter.assert_called_with(Q())

        Q.reset_mock()
        self.search_with_2(self.cls, "firstname:exact", "Susan", self.sql_query, None)
        Q.assert_has_calls(
            [call(name="Susan"), call(lastname="Susan"), call().__ior__(Q())]
        )
        self.sql_query.filter.assert_called_with(Q().__ior__())


###
# PyMODM
###
class TestPyModmNumeric(unittest.TestCase):
    def setUp(self):
        self.NumericSearch = searches_pymodm.NumericSearch
        column = Mock()
        self.column = column
        self.cls = SimpleNamespace(name=column)
        self.sql_query = Mock()
        self.search = self.NumericSearch("age")

    def test_to_float(self):
        self.assertEqual(searches_pymodm.to_float("2"), 2.0)
        with self.assertRaises(QueryValidationError) as e:
            searches_pymodm.to_float("nope")
        self.assertEqual(e.exception.args[0], "nope is an invalid numerical parameter")

    @patch("fhirbug.db.backends.pymodm.searches.to_float")
    def test_numeric_search(self, to_float):
        ret = self.search(self.cls, "", "lt2", self.sql_query, "")
        to_float.assert_called_with("2")
        self.sql_query.raw.assert_called_with({"age": {"$lt": to_float()}})

        ret = self.search(self.cls, "", "gt2.123", self.sql_query, "")
        to_float.assert_called_with("2.123")
        self.sql_query.raw.assert_called_with({"age": {"$gt": to_float()}})

        ret = self.search(self.cls, "", "le1002.112323", self.sql_query, "")
        to_float.assert_called_with("1002.112323")
        self.sql_query.raw.assert_called_with({"age": {"$lte": to_float()}})

        ret = self.search(self.cls, "", "ge.3", self.sql_query, "")
        to_float.assert_called_with(".3")
        self.sql_query.raw.assert_called_with({"age": {"$gte": to_float()}})

        ret = self.search(self.cls, "", "eq1.3", self.sql_query, "")
        to_float.assert_called_with("1.3")
        self.sql_query.raw.assert_called_with({"age": to_float()})

        ret = self.search(self.cls, "", "ne1.3", self.sql_query, "")
        to_float.assert_called_with("1.3")
        self.sql_query.raw.assert_called_with({"age": {"$ne": to_float()}})

        ret = self.search(self.cls, "", "ap100.123", self.sql_query, "")
        to_float.assert_called_with("100.123")
        self.sql_query.raw.assert_called_with({"age": {"$gte": to_float().__sub__()}})
        self.sql_query.raw().raw.assert_called_with(
            {"age": {"$lte": to_float().__add__()}}
        )

        ret = self.search(self.cls, "", "101.123", self.sql_query, "")
        to_float.assert_called_with("101.123")
        self.sql_query.raw.assert_called_with({"age": to_float()})


@patch("fhirbug.db.backends.pymodm.searches.NumericSearch")
class TestPyModmNumericSearchWithQuantity(unittest.TestCase):
    def test_it(self, NSMock):
        cv = Mock()
        aq = Mock()
        search = searches_pymodm.NumericSearchWithQuantity("value", convert_value=cv)
        search("a", "a", "eq123|mg", "f", "query")
        cv.assert_called_with("eq123", "mg")
        aq.assert_not_called()
        NSMock.assert_called_with("value")
        NSMock().search.assert_called_with("a", "a", cv(), "f", "query")

        cv = Mock()
        aq = Mock()
        search = searches_pymodm.NumericSearchWithQuantity("value", alter_query=aq)
        search("a", "a", "eq123|mg", "f", "query")
        cv.assert_not_called()
        aq.assert_called_with("query", "eq123", "mg")
        NSMock.assert_called_with("value")
        NSMock().search.assert_called_with("a", "a", "eq123", aq(), "query")

        cv = Mock()
        aq = Mock()
        search = searches_pymodm.NumericSearchWithQuantity(
            "value", convert_value=cv, alter_query=aq
        )
        search("a", "a", "eq123|http://unitsofmeasure.org|mg", "f", "query")
        cv.assert_called_with("eq123", "http://unitsofmeasure.org|mg")
        aq.assert_called_with("query", cv(), "http://unitsofmeasure.org|mg")
        NSMock.assert_called_with("value")
        NSMock().search.assert_called_with("a", "a", cv(), aq(), "query")
