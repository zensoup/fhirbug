import unittest
from fhirball.server.requestparser import parse_url, split_join
from fhirball.exceptions import QueryValidationError


class TestSplitJoin(unittest.TestCase):
    def test_split_join(self):
        lst = ['a', 'a,b', 'a,b,c']
        self.assertEquals(split_join(lst), ['a', 'a', 'b', 'a', 'b', 'c'])

        lst = ['a']
        self.assertEquals(split_join(lst), ['a'])

        lst = ['a,b,c,d']
        self.assertEquals(split_join(lst), ['a', 'b', 'c', 'd'])


class TestUrlParsing(unittest.TestCase):
    def test_resource(self):
        url = "Patient"
        query = parse_url(url)
        self.assertEquals(query.resource, "Patient")

        url = "Patient/"
        query = parse_url(url)
        self.assertEquals(query.resource, "Patient")

        url = ""
        query = parse_url(url)
        self.assertEquals(query.resource, None)

        url = "/"
        query = parse_url(url)
        self.assertEquals(query.resource, None)

    def test_resourceId(self):
        url = "Patient/123"
        query = parse_url(url)
        self.assertEquals(query.resource, "Patient")
        self.assertEquals(query.resourceId, "123")

    def test_operation(self):
        url = "Patient/123/_history"
        query = parse_url(url)
        self.assertEquals(query.resource, "Patient")
        self.assertEquals(query.resourceId, "123")
        self.assertEquals(query.operation, "_history")

    def test_operationId(self):
        url = "Patient/123/_history/1"
        query = parse_url(url)
        self.assertEquals(query.resource, "Patient")
        self.assertEquals(query.resourceId, "123")
        self.assertEquals(query.operation, "_history")
        self.assertEquals(query.operationId, "1")

    def test_base_operation(self):
        url = "Patient/_history"
        query = parse_url(url)
        self.assertEquals(query.resource, "Patient")
        self.assertEquals(query.resourceId, None)
        self.assertEquals(query.operation, "_history")

        url = "Patient/_search"
        query = parse_url(url)
        self.assertEquals(query.resource, "Patient")
        self.assertEquals(query.resourceId, None)
        self.assertEquals(query.operation, "_search")


class TestParameterParsing(unittest.TestCase):
    def test_modifiers(self):
        url = "Patient?_count=12"
        query = parse_url(url)
        self.assertEquals(query.resource, "Patient")
        self.assertEquals(query.resourceId, None)
        self.assertEquals(query.operation, None)
        self.assertEquals(query.modifiers, {"_count": ["12"]})
        self.assertEquals(query.search_params, {})

        url = "Observation?_count=12&_include=Observation:Subject"
        query = parse_url(url)
        self.assertEquals(query.resource, "Observation")
        self.assertEquals(query.resourceId, None)
        self.assertEquals(query.operation, None)
        self.assertEquals(
            query.modifiers, {"_count": ["12"], "_include": ["Observation:Subject"]}
        )
        self.assertEquals(query.search_params, {})

    def test_modifiers_comma_sep(self):
        url = "Observation?_count=12&_include=Observation:Subject,Observation:Recommender"
        query = parse_url(url)
        self.assertEquals(
            query.modifiers, {"_count": ["12"], "_include": ["Observation:Subject", "Observation:Recommender"]}
        )

    def test_modifiers_and_searches(self):
        url = "Observation?subject.name=John&_count=12&_include=Observation:Subject"
        query = parse_url(url)
        self.assertEquals(query.resource, "Observation")
        self.assertEquals(query.resourceId, None)
        self.assertEquals(query.operation, None)
        self.assertEquals(
            query.modifiers, {"_count": ["12"], "_include": ["Observation:Subject"]}
        )
        self.assertEquals(query.search_params, {"subject.name": ["John"]})
