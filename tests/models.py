from fhirbug.models.mixins import FhirBaseModelMixin, FhirAbstractBaseMixin
from fhirbug.models.attributes import (
    Attribute,
    const,
    DateAttribute,
    ReferenceAttribute,
)
from unittest.mock import Mock
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


class AttributeWithPropertyGetterAndSetter:
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
    _name = "my_name"

    class FhirMap:
        def search_name(cls, field_name, value, sql_query, query):
            return sql_query

        name = Attribute(searcher=search_name)


class WithSearcherAndRegex(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _name = "my_name"

    class FhirMap:
        def search_name(cls, field_name, value, sql_query, query):
            return sql_query

        name = Attribute(searcher=search_name, search_regex=r"(name|NAME)")


class BaseMixinModel(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _name = "hello"
    _age = 12
    __Resource__ = "Patient"

    class FhirMap:
        active = Attribute(const(True))
        name = Attribute("_name", "_name")
        age = Attribute("_age", "_age")


class BetterBaseMixinModel(FhirAbstractBaseMixin, FhirBaseModelMixin):
    from fhirbug.Fhir.resources import HumanName

    _name = HumanName(family="sponge", given="bob")
    _age = 12
    __Resource__ = "Patient"

    class FhirMap:
        active = Attribute(const(True))
        name = Attribute("_name", "_name")
        age = Attribute("_age", "_age")


ReferenceTarget_get_orm_query = Mock()
class ReferenceTarget(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _name = "my_name"
    _get_orm_query = ReferenceTarget_get_orm_query

    class FhirMap:
        name = Attribute("_name")


class WithReference(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _model = SN(ref_id=12, _contained_names=[])

    ref = ReferenceAttribute(ReferenceTarget, "ref_id", "ref")


class WithReferenceAndDisplay(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _model = SN(ref_id=12, _contained_names=[])

    ref = ReferenceAttribute(ReferenceTarget, "ref_id", "ref", force_display=True)


class WithReferenceAndContained(FhirAbstractBaseMixin, FhirBaseModelMixin):
    _model = SN(ref_id=12, _contained_names=["ref"], _refcount=0, _contained_items=[])

    ref = ReferenceAttribute(ReferenceTarget, "ref_id", "ref")
