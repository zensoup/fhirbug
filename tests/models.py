from fhirbug.models.mixins import FhirBaseModelMixin, FhirAbstractBaseMixin
from fhirbug.models.attributes import (
    Attribute,
    const,
    DateAttribute,
    ReferenceAttribute,
    BooleanAttribute,
    NameAttribute,
)
from fhirbug.constants import AUDIT_SUCCESS, AUDIT_MINOR_FAILURE
from unittest.mock import Mock, MagicMock
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
    _model = None
    name = Attribute(const("the_name"))


class AttributeWithConstSetter:
    _model = SN(_name=12)
    name = Attribute('_name', ('_name', const("the_name")))


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


MixinModelWithSetters_after_update = Mock()
MixinModelWithSetters_after_create = MagicMock(side_effect=lambda x: x)


class MixinModelWithSetters(FhirAbstractBaseMixin, FhirBaseModelMixin):
    from fhirbug.Fhir.resources import HumanName

    __Resource__ = "Patient"
    _name = HumanName(family="sponge", given="bob")
    _active = True
    _after_update = MixinModelWithSetters_after_update
    _after_create = MixinModelWithSetters_after_create

    class FhirMap:
        name = Attribute("_name", "_name")
        active = Attribute("_active", "_active")


Auditing_audit_update_success = MagicMock(
    side_effect=lambda x: SN(outcome=AUDIT_SUCCESS)
)
Auditing_audit_update_failure = MagicMock(
    side_effect=lambda x: SN(outcome=AUDIT_MINOR_FAILURE)
)
Auditing_audit_create_success = MagicMock(
    side_effect=lambda x: SN(outcome=AUDIT_SUCCESS)
)
Auditing_audit_create_failure = MagicMock(
    side_effect=lambda x: SN(outcome=AUDIT_MINOR_FAILURE)
)
Auditing_after_create = MagicMock(side_effect=lambda x: x)


class MixinModelWithSettersAndAuditing(FhirAbstractBaseMixin, FhirBaseModelMixin):
    from fhirbug.Fhir.resources import HumanName

    __Resource__ = "Patient"
    _name = HumanName(family="sponge", given="bob")
    _active = True
    _after_update = Mock()
    _after_create = Auditing_after_create
    audit_update = Auditing_audit_update_success
    audit_create = Auditing_audit_create_success

    class FhirMap:
        name = Attribute("_name", "_name")
        active = Attribute("_active", "_active")


class MixinModelWithSettersAndAuditingProtected(
    FhirAbstractBaseMixin, FhirBaseModelMixin
):
    _name = None
    _active = None

    _after_update = Mock()
    _after_create = MagicMock(side_effect=lambda x: x)
    __Resource__ = "Patient"

    def audit_update(self, query):
        self.protect_attributes(["active"])
        return SN(outcome=AUDIT_SUCCESS)

    def audit_update2(self, query):
        self.hide_attributes(["active"])
        return SN(outcome=AUDIT_SUCCESS)

    def audit_create(self, query):
        self.protect_attributes(["active"])
        return SN(outcome=AUDIT_SUCCESS)

    def audit_create2(self, query):
        self.hide_attributes(["active"])
        return SN(outcome=AUDIT_SUCCESS)

    class FhirMap:
        name = Attribute("_name", "_name")
        active = Attribute("_active", "_active")


DeletableMixinModel_delete_method = Mock()


class DeletableMixinModel(BaseMixinModel, FhirAbstractBaseMixin, FhirBaseModelMixin):
    @classmethod
    def _delete_item(cls, item):
        return DeletableMixinModel_delete_method(cls, item)


DeletableMixinModelAudited_delete_method = Mock()
Auditing_audit_delete_success = MagicMock(
    side_effect=lambda x: SN(outcome=AUDIT_SUCCESS)
)
Auditing_audit_delete_failure = MagicMock(
    side_effect=lambda x: SN(outcome=AUDIT_MINOR_FAILURE)
)


class DeletableMixinModelAudited(
    BaseMixinModel, FhirAbstractBaseMixin, FhirBaseModelMixin
):
    audit_delete = Auditing_audit_delete_success

    @classmethod
    def _delete_item(cls, item):
        return DeletableMixinModelAudited_delete_method(cls, item)


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


class BooleanAttributeModel:
    _model = SN(toast=0, yellow=False, feather="true", something="cheese", deflt="asdf")
    toast = BooleanAttribute("toast", "toast")
    yellow = BooleanAttribute("yellow", "yellow")
    feather = BooleanAttribute(("feather", str), "yellow")
    true = BooleanAttribute(const(True))
    deflt = BooleanAttribute("deflt", default=False)
    something = BooleanAttribute("something")


class NameAttibuteModel:
    givenSetterMock = Mock()
    _model = SN(_given1="sponge", _given2="bob", _family="squarepants")
    withSetters = NameAttribute(
        given_getter="_given1",
        given_setter="_given1",
        family_getter="_family",
        family_setter="_family",
    )
    withJoin = NameAttribute(
        given_getter="_given1",
        given_setter="_given1",
        family_getter="_family",
        family_setter="_family",
        join_given_names=True,
    )
    withPass = NameAttribute(
        given_getter="_given1",
        given_setter=givenSetterMock,
        family_getter="_family",
        family_setter="_family",
        pass_given_names=True,
    )
