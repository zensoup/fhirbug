import builtins
from importlib import import_module
from fhirbug.exceptions import (
    MappingValidationError,
    UnsupportedOperationError,
    MappingException,
)
from fhirbug.Fhir import resources as fhir
from fhirbug.config import import_searches, import_models, settings
from fhirbug.server import get_request_context


def audited(func):
    """
    A decorator that adds auditing functionality to the ``__get__`` and ``__set__`` methods of descriptor Attributes.
    Attribute auditors, depending on the result of the audit, can return ``True``, meaning access to the attribute has
    been granted or ``False``, meaning access has been denied but execution should continue normally. If execution
    should stop and an error returned to the requester, it should raise an exception.
    """

    def with_audit(desc, instance, arg):
        # __set__ does not receive an owner argument owner
        if func.__name__ == "__set__":
            own = instance.__class__
            method = "audit_set"
        else:
            own = arg
            method = "audit_get"

        ctx = get_request_context()
        prop_name = getattr(desc, "_attribute_name", "")
        if (
            hasattr(desc, method)
            and ctx is not None
            and getattr(desc, method) is not None
        ):
            res = getattr(desc, method)(instance._model, ctx, prop_name)
            if res != True:
                return None
        return func(desc, instance, arg)

    return with_audit


class Attribute:
    """
    The base class for declaring db to fhir mappings. Accepts three positional arguments, a getter, a setter and a searcher.

    Getting values
    --------------

    The getter parameter can be a string, a tuple, a callable or type const.

    - Using a string:

    >>> from types import SimpleNamespace as SN
    >>> class Bla:
    ...   _model = SN(column_name=12)
    ...   p = Attribute('column_name')
    ...
    >>> b = Bla()
    >>> b.p
    12

    - Strings can also be properties:

    >>> class Model:
    ...  column_name = property(lambda x: 13)
    >>> class Bla:
    ...   _model = Model()
    ...   p = Attribute('column_name')
    ...
    >>> b = Bla()
    >>> b.p
    13

    - Callables will be called:

    >>> class Bla:
    ...   _model = SN(column_name=12)
    ...   def get_col(self):
    ...     return 'test'
    ...   p = Attribute(get_col)
    ...
    >>> b = Bla()
    >>> b.p
    'test'

    - As a shortcut, a tuple (col_name, callable) can be passed. The result will be callable(_model.col_name)

    >>> import datetime
    >>> class Bla:
    ...  _model = SN(date='2012')
    ...  p = Attribute(('date', int))
    ...
    >>> b = Bla()
    >>> b.p
    2012

    Setting values
    --------------

    The setter parameter can be a string, a tuple, a callable or type const.

    - Using a string:

    >>> class Bla:
    ...  _model = SN(date='2012')
    ...  p = Attribute(setter='date')
    ...
    >>> b = Bla()
    >>> b.p = '2013'
    >>> b._model.date
    '2013'

    - Again, the string can point to a property with a setter:

    >>> class Model:
    ...  b = 12
    ...  def set_b(self, value):
    ...    self.b = value
    ...  column_name = property(lambda self: self.b, set_b)
    >>> class Bla:
    ...   _model = Model()
    ...   p = Attribute(getter='column_name', setter='column_name')
    ...
    >>> b = Bla()
    >>> b.p = 13
    >>> b.p == b._model.b == 13
    True

    - Callables will be called:

    >>> class Bla:
    ...   _model = SN(column_name=12)
    ...   def set_col(self, value):
    ...     self._model.column_name = value
    ...   p = Attribute(setter=set_col)
    ...
    >>> b = Bla()
    >>> b.p = 'test'
    >>> b._model.column_name
    'test'

    - Two-tuples contain a column name and a callable or const. Set the column to the result of the callable or const

    >>> def add(column, value):
    ...  return column + value

    >>> class Bla:
    ...   _model = SN(column_name=12)
    ...   p = Attribute(setter=('column_name', add))
    ...
    >>> b = Bla()
    >>> b.p = 3
    >>> b._model.column_name
    15
    """

    def __init__(
        self,
        getter=None,
        setter=None,
        searcher=None,
        search_regex=None,
        audit_get=None,
        audit_set=None,
    ):
        self.getter = getter
        self.setter = setter
        self.searcher = searcher
        self.audit_get = audit_get
        self.audit_set = audit_set
        if search_regex:
            self.search_regex = search_regex

    @audited
    def __get__(self, instance, owner):
        getter = self.getter
        # Strings are column names
        if isinstance(getter, str):
            return getattr(instance._model, getter)
        # Consts provide a constant value
        if isinstance(getter, const):
            return getter.value
        # Callables should be called
        if callable(getter):
            return getter(instance)
        # Two-tuples contain a column name and a callable. Pass the column value to the callable
        if isinstance(getter, (tuple, list)):
            column, func = getter
            return func(getattr(instance._model, column))

    @audited
    def __set__(self, instance, value):
        try:
            setter = self.setter
            assert setter is not None
        except (AttributeError, AssertionError):
            if settings.STRICT_MODE.get("set_attribute_without_setter", False):
                raise UnsupportedOperationError(
                    "You are trying to alter an attribute that can not be changed"
                )
            else:
                # TODO: log
                return

        # Strings are column names
        if isinstance(setter, str):
            setattr(instance._model, setter, value)
        # Callables should be called
        if callable(setter):
            setter(instance, value)
        # Two-tuples contain a column name and a callable or const. Set the column to the result of the callable or const
        if isinstance(setter, (tuple, list)):
            column, func = setter
            if isinstance(func, const):
                setattr(instance._model, column, func.value)
            else:
                res = func(getattr(instance._model, column), value)
                setattr(instance._model, column, res)

    def __set_name__(self, owner, name):
        """
        Save the name this descriptor has been assigned to
        """
        self._attribute_name = name

    def _get_property_name(self, owner_cls):
        """
        .. deprecated:: 0.1.2

        Deprecated: Use ``self._attribute_name`` instead.

        Traverses the class's inheritance tree and finds the property name
        this Attribute has been assigned to. This is useful because the property
        name is the name of the the Fhir attribute the property represents.

        :param: class owner_cls The class that owns this property
        :returns: The Fhir name this Attribute has been assigned to.
        :r_type: str
        """
        if not owner_cls:
            return
        for cls in owner_cls.mro()[:-1]:
            for k, v in vars(cls).items():
                if id(v) == id(self):
                    return k


class const:
    """
    const can be used as a getter for an attribute that should always return the same value

    >>> from types import SimpleNamespace as SN
    >>> class Bla:
    ...   p = Attribute(const(12))
    ...
    >>> b = Bla()
    >>> b.p
    12
    """

    def __init__(self, value):
        self.value = value


class BooleanAttribute(Attribute):
    """
    Used for attributes representing boolean types.
    ``truthy_values`` and ``falsy_values`` are used to determine which possible values from the database
    we should consider as True and False.
    Values that are not in any of the lists are mapped to ``default`` and if that is None, a MappingValidationError is
    thrown.

    :param save_true_as: How do we save True in the database
    :param save_false_as: How do we save Fasle in the database
    :param deafult: If we read a value that is not in ``truthy_values`` or ``falsy_values``, it will default to ths value.
    :param list truthy_values: Which values, when read from the database should be mapped to True
    :param list falsy_values: Which values, when read from the database should be mapped to False
    """

    def __init__(
        self,
        *args,
        save_true_as=1,
        save_false_as=0,
        default=None,
        truthy_values=["true", "True", 1, "1"],
        falsy_values=["false", "False", "0", 0],
        **kwargs,
    ):
        self.save_true_as = save_true_as
        self.save_false_as = save_false_as
        self.truthy_values = truthy_values
        self.falsy_values = falsy_values
        self.default = default
        return super(BooleanAttribute, self).__init__(*args, **kwargs)

    def __get__(self, *args, **kwargs):
        value = super(BooleanAttribute, self).__get__(*args, **kwargs)
        if value in self.truthy_values:
            return True
        elif value in self.falsy_values:
            return False
        else:
            return self.default

    def __set__(self, instance, value):
        if value:
            value = self.save_true_as
        else:
            value = self.save_false_as
        super(BooleanAttribute, self).__set__(instance, value)


class ReferenceAttribute(Attribute):
    """
    A Reference to some other Resource that may be contained.
    """

    def __init__(self, cls, id, name, setter=None, force_display=False, searcher=None):
        self.cls = cls
        self.id = id
        self.name = name
        self.setter = setter
        self.force_display = force_display
        self.searcher = searcher

    def __get__(self, instance, owner):
        cls_name = self.cls.__name__
        id = getattr(instance._model, self.id)

        if (
            self.name in instance._model._contained_names
        ):  # The resource should be contained
            # Get the item
            item = self.cls._get_orm_query().get(id)

            # TODO: try..catch
            as_fhir = item.to_fhir()

            instance._model._refcount += 1

            as_fhir.id = f"ref{instance._model._refcount}"
            instance._model._contained_items.append(as_fhir)

            # Build the reference dict
            reference = {"reference": f"#ref{instance._model._refcount}"}

            # Add a display if possible
            if hasattr(item, "_as_display"):
                reference["display"] = item._as_display()

            return reference

        else:  # The resource is not contained, generate a url

            # Build the reference dict
            reference = {
                "reference": f"{cls_name}/{id}",
                "identifier": {"system": f"{cls_name}", "value": str(id)},
            }

            if self.force_display:  # Do a query to fetch the display
                # TODO: can we check if it supprts `_as_display` before querying?

                item = self.cls._get_orm_query().get(id)

                if hasattr(item, "_as_display"):
                    reference["display"] = item._as_display()

            return reference

    def __set__(self, instance, reference):
        value = None
        try:
            # TODO: can we make this all a user-defined parameter for the entire identifier?
            sys = reference.identifier.system
            # assigner = reference.identifier.assigner
            value = reference.identifier.value
        except AttributeError:
            pass

        if hasattr(reference, "reference"):
            ref = reference.reference
            if ref.startswith("#"):
                # TODO read internal reference
                pass

        if value is None:
            raise MappingValidationError("Invalid reference")

        if self.setter:
            Attribute(setter=self.setter).__set__(instance, value)


class DateAttribute(Attribute):
    def __init__(self, field, audit_get=None, audit_set=None):
        self.audit_get = audit_get
        self.audit_set = audit_set
        searches = import_searches()

        def setter(old_date_str, new_date_str):
            if hasattr(new_date_str, "strftime"):
                return fhir.FHIRDate(new_date_str).date
            if isinstance(new_date_str, str):
                return fhir.FHIRDate(new_date_str).date
            elif isinstance(new_date_str, fhir.FHIRDate):
                return new_date_str.date

        self.getter = (field, fhir.FHIRDate)
        self.setter = (field, setter)
        self.searcher = searches.DateSearch(field)


class NameAttribute(Attribute):
    """
    NameAttribute is for used on fields that represnt a HumanName resource.
    The parameters can be any of the valid getter and setter types for
    simple :class:`Attribute`

    :param family_getter: A getter type parameter for the family name.
    :param given_getter: A getter type parameter for the given name
    :param family_setter: A setter type parameter for the family name
    :param given_setter: A getter type parameter for the given name
    """

    def __init__(
        self,
        family_getter=None,
        given_getter=None,
        family_setter=None,
        given_setter=None,
        join_given_names=False,
        pass_given_names=False,
        getter=None,
        setter=None,
        searcher=None,
        given_join_separator=" ",
        audit_get=None,
        audit_set=None,
    ):
        self.audit_get = audit_get
        self.audit_set = audit_set
        searches = import_searches()
        if join_given_names and pass_given_names:
            raise MappingException(
                "You can not pass both pass_given_names and join_given_names. Only one of these arguments is allowed to be True"
            )

        def _getter(instance):
            family = Attribute(family_getter).__get__(instance, None)
            given = Attribute(given_getter).__get__(instance, None)
            return fhir.HumanName(family=family, given=given)

        def _setter(instance, humanNames):
            family = humanNames[0].family

            if join_given_names:
                given = given_join_separator.join(humanNames[0].given)
            elif pass_given_names:
                given = humanNames[0].given
            else:
                given = humanNames[0].given[0]

            Attribute(setter=family_setter).__set__(instance, family)
            Attribute(setter=given_setter).__set__(instance, given)

        def _searcher(cls, field_name, value, sql_query, query):
            # TODO: only works with string fields
            if "family" in field_name:
                return searches.StringSearch(family_getter)(
                    cls, field_name, value, sql_query, query
                )
            if "given" in field_name:
                return searches.StringSearch(given_getter)(
                    cls, field_name, value, sql_query, query
                )
            return searches.StringSearch(family_getter, given_getter)(
                cls, field_name, value, sql_query, query
            )

        self.getter = getter or _getter
        self.setter = setter or _setter
        self.searcher = searcher or _searcher
        self.search_regex = r"(family|given|name)(:\w*)?"


class EmbeddedAttribute(Attribute):
    """
    An attribute representing a BackboneElement that is described by a model
    and is stored using an ORM relationship, usually a ForeignKeyField or
    an embedded mongo document.
    """

    def __init__(self, *args, type=None, **kwargs):
        if type is None:
            raise MappingValidationError(
                "You hane defined an EmbeddedAttribute without specifying the type."
            )

        self._type = type
        super(EmbeddedAttribute, self).__init__(*args, **kwargs)

    @property
    def type(self):
        # If a class name has been passed as a string, import the model
        _type = self._type
        if type(_type) is str:
            models = import_models()
            _type = getattr(models, _type)
        return _type


    def __get__(self, instance, owner):
        # Let the ORM handle getting the backbone element. The ORM should return
        # a Fhirbug map.
        embedded_resource = super(EmbeddedAttribute, self).__get__(instance, owner)
        if embedded_resource is None:
            return None
        # Handle lists
        if type(embedded_resource) is list:
            return [r.to_fhir() for r in embedded_resource]
        # Return a fhir resource
        return embedded_resource.to_fhir()

    def __set__(self, instance, value):
        """
        We accept a Fhir Resource class when handling requests
        but we also allow setting the value using a dictionary.
        We convert to a Fhir Map and set.
        """
        if type(value) is dict:
            value = self.dict_to_resource(value)
            embedded_resource = self.type.from_resource(value)
        elif type(value) is list:
            embedded_resource = map(
                lambda v: self.type.from_resource(self.dict_to_resource(v))
                if type(v) is dict
                else self.type.from_resource(v),
                value,
            )
        else:
            embedded_resource = self.type.from_resource(value)
        return super(EmbeddedAttribute, self).__set__(instance, embedded_resource)

    def dict_to_resource(self, dict):
        """
        Convert a dictionary to an instance of the corresponding FHIR resource
        """
        mapperClass = self.type
        ResourceClass = mapperClass._get_resource_cls()
        return ResourceClass(dict)
