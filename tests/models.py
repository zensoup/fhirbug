from fhirbug.models.mixins import FhirBaseModelMixin, FhirAbstractBaseMixin
from fhirbug.models.attributes import Attribute, const, DateAttribute
from types import SimpleNamespace as SN


class AttributeWithStringGetter:
    _model = SN(name="my_name")
    name = Attribute("name")


class AttributeWithStringGetterAndSetter:
    _model = SN(name="my_name")
    name = Attribute("name", "name")


class AttributeWithPropertyGetter:
    class Model:
        name = property(lambda self: "my_name")

    _model = Model()
    name = Attribute("name")


class AttributeWithPropertyGetterAndGetter:
    class Model:
        _name = "my_name"

        def set_name(self, value):
            self._name = value

        name = property(lambda self: self._name, set_name)

    _model = Model()
    name = Attribute("name", "name")


class AttributeWithCallables:
    _model = SN(name="my_name")

    def get_name(self):
        return self._model.name

    def set_name(self, value):
        self._model.name = value

    name = Attribute(get_name, set_name)


class AttributeWithTransformerGetter:
    _model = SN(name="my_name")
    name = Attribute(("name", lambda x: x.upper()))


class AttributeWithTransformerSetter:
    _model = SN(name="my_name")
    name = Attribute("name", ("name", lambda curr, new: new.upper()))


class AttributeWithConst:
    name = Attribute(const("the_name"))


class WithDateAttribute:
    from datetime import datetime

    _model = SN(the_date=datetime(2012, 12, 12))
    date = DateAttribute("the_date")


class WithSearcher(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _name = 'my_name'
    class FhirMap:
        def search_name(cls, field_name, value, sql_query, query):
            return sql_query
        name = Attribute(searcher=search_name)


class WithSearcherAndRegex(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _name = 'my_name'
    class FhirMap:
        def search_name(cls, field_name, value, sql_query, query):
            return sql_query
        name = Attribute(searcher=search_name, search_regex=r'(name|NAME)')


class BaseMixinModel(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _name = "hello"
    _age = 12
    __Resource__ = 'Patient'

    class FhirMap:
        active=Attribute(const(True))
        name = Attribute("_name", "_name")
        age = Attribute("_age", "_age")


class BetterBaseMixinModel(FhirAbstractBaseMixin, FhirBaseModelMixin):
    from fhirbug.Fhir.resources import HumanName
    _name = HumanName(family="sponge", given="bob")
    _age = 12
    __Resource__ = 'Patient'

    class FhirMap:
        active=Attribute(const(True))
        name = Attribute("_name", "_name")
        age = Attribute("_age", "_age")
