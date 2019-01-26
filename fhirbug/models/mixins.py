import re

from fhirbug.constants import AUDIT_SUCCESS
from fhirbug.Fhir import resources
from fhirbug.models.attributes import Attribute
from fhirbug.config import import_models
from fhirbug.exceptions import (
    DoesNotExistError,
    MappingValidationError,
    AuthorizationError,
)
from fhirbug.Fhir.resources import PaginatedBundle

from fhirbug.config import settings


class FhirAbstractBaseMixin:
    """
    Adds additional fhir related functionality to all models.
    Most importantly, it provides the  ``.to_fhir()`` method that
    handles the transformation from an SQLAlchemy model to a Fhir resource.
    User-defined models subclassing this class **must** implement a ``FhirMap``
    nested class.
    """

    def to_fhir(self, *args, query=None, **kwargs):
        """
        Convert from a BaseModel to a Fhir Resource and return it.

        If param `query` is passed and is of type server.FhirRequestQuery, it is used to
        allow for additional functionality like contained resources.
        """

        # Initialize attributes
        self._searchables = []
        self._contained_names = query.modifiers.get("_include", []) if query else []
        self._elements = query.modifiers.get("_elements", None) if query else None
        self._contained_items = []
        self._refcount = 0

        # Use __Resource__ if it has been defined else the dame of the class
        resource_name = getattr(self, "__Resource__", self.__class__.__name__)
        Resource = getattr(resources, resource_name)

        # Filter the matching fields
        param_dict = self.get_params_dict(Resource, elements=self._elements)

        # Cast to a resource
        resource = Resource(param_dict, strict=kwargs.get("strict", True))

        self.get_rev_includes(query)

        # Add any contained items that have been generated
        if self._contained_items:
            resource.contained = self._contained_items

        return resource

    def get_params_dict(self, resource, elements=None):
        """
        Return a dictionary of all valid values this instance can provide for a resource of the type ``resource``.

        :param resource: The class of the resource we wish to create
        :return: A dictionary to be used as an argument to initialize a resource instance
        """
        # TODO: Allow for a fields attribute to manually specify which fields to be used?

        # Read this instances available attributes
        attributes = [prop for prop in dir(self.Fhir) if not prop.startswith("_")]

        # Create a mock resource for comparison
        mock = resource()

        # If the _elements paramater has been passed, return the elements specified there,
        # along with all mandatory ones
        # TODO: toggle inclusion of mandatory based on a setting
        if elements:
            attributes = [
                attr
                for attr in attributes
                if attr in elements + mock.mandatoryFields() + ["id"]
            ]

        hidden_attrs = getattr(self, "_hidden_attributes", [])
        hidden_attrs = list(map(lambda x: x.lower(), hidden_attrs))

        # Evaluate the common attributes. This is where all the getters are called
        param_dict = {
            attribute: getattr(self.Fhir, attribute)
            for attribute in attributes
            if hasattr(mock, attribute)
            and attribute.lower() not in hidden_attrs
        }
        return param_dict

    def get_rev_includes(self, query):
        """
        Read the _revincludes that were asked for in the request, query the database to retrieve
        them and add them to the initial resources ``contained`` field.

        :param query: A :class:`FhirRequestQuery` object holding the current request.
        :type query: :class:`fhirbug.server.requestparser.FhirRequestQuery`

        :returns: None
        """
        if query and "_revinclude" in query.modifiers:
            models = import_models()
            revincludes = query.modifiers.get("_revinclude")
            for rev in revincludes:
                resource_name, field, *_ = rev.split(":")
                Resource = getattr(models, resource_name)
                # sql_query = cls.searchables()[search](cls, search, value, sql_query, query)
                if field in Resource.searchables():
                    items = Resource.searchables()[field](
                        Resource, field, self.Fhir.id, Resource._get_orm_query(), query
                    ).all()
                    self._contained_items += list(map(lambda i: i.to_fhir(), items))

    @classmethod
    def create_from_resource(cls, resource, query=None):
        """
        Creates and saves a new row from a Fhir.Resource object
        """

        obj = cls()
        obj.Fhir._query = query

        # Audit the creation if implemented
        if hasattr(obj, "audit_create"):
            auditEvent = obj.audit_create(query)
            if auditEvent.outcome != AUDIT_SUCCESS:
                raise AuthorizationError(auditEvent=auditEvent)

        # Get the protected fields
        protected_attrs = getattr(obj, "_protected_attributes", [])

        # Read the attributes of the FhirMap class
        own_attributes = [
            prop
            for prop, type in cls.FhirMap.__dict__.items()
            if isinstance(type, Attribute)
            and prop not in protected_attrs
        ]

        for path in own_attributes:
            value = getattr(resource, path.replace("_", "."), None)
            if value is not None:
                setattr(obj.Fhir, path, value)

        obj = cls._after_create(obj)
        return obj

    def update_from_resource(self, resource, query=None):
        """
        Edits an existing row from a Fhir.Resource object
        """

        # Audit the update if implemented
        if hasattr(self, "audit_update"):
            auditEvent = self.audit_update(query)
            if auditEvent.outcome != AUDIT_SUCCESS:
                raise AuthorizationError(auditEvent=auditEvent)

        # Get the protected fields
        protected_attrs = getattr(self, "_protected_attributes", [])

        # Read the attributes of the FhirMap class
        own_attributes = [
            prop
            for prop, type in self.FhirMap.__dict__.items()
            if isinstance(type, Attribute)
            and prop not in protected_attrs
        ]

        self.Fhir._query = query

        # for path in own_attributes:
        for path in own_attributes:
            value = getattr(resource, path.replace("_", "."), None)
            if value is not None:
                setattr(self.Fhir, path, value)

        new = self.__class__._after_update(self)
        return new

    @classmethod
    def delete_item(cls, item, query=None):
        # Audit the update if needed
        if hasattr(item, "audit_delete"):
            auditEvent = item.audit_delete(query)
            if auditEvent.outcome != AUDIT_SUCCESS:
                raise AuthorizationError(auditEvent=auditEvent)
        return cls._delete_item(item)


    def protect_attributes(self, attribute_names=[]):
        """
        Accepts a list of attribute names and protects them for the duration of the current operation.
        Protected attributes can not be changed when creating or editing a resource.
        Subsequent calls replace the previous attribute list.

        :param list attribute_names: A list of Fhir attribute names to set as protected
        """
        self._protected_attributes = attribute_names

    def hide_attributes(self, attribute_names=[]):
        """
        Accepts a list of attribute names and marks them as hidden, meaning they will not be included in json
        representations of this item.
        Subsequent calls replace the previous attribute list.

        :param list attribute_names: A list of Fhir attribute names to set as hidden
        """
        self._hidden_attributes = attribute_names


class FhirBaseModelMixin:
    @classmethod
    def get(cls, query, *args, **kwargs):
        """
        Handle a GET request
        """
        if query.resourceId:
            # item = cls._get_orm_query().get(query.resourceId)
            try:
                item = cls._get_item_from_pk(query.resourceId)
            except DoesNotExistError:
                raise MappingValidationError(
                    f'Resource "{query.resource}/{query.resourceId}" does not exist.'
                )
            if hasattr(item, "audit_read"):
                auditEvent = item.audit_read(query)
                if auditEvent.outcome != AUDIT_SUCCESS:
                    raise AuthorizationError(auditEvent=auditEvent)
            res = item.to_fhir(*args, query=query, **kwargs)
            return res.as_json()

        else:
            # Handle search
            sql_query = cls._get_orm_query()
            for search in [
                *query.search_params,
                *query.modifiers,
            ]:  # TODO: Do we really need to check the modifiers here?
                if cls.has_searcher(search):
                    values = query.search_params.get(
                        search, query.modifiers.get(search)
                    )
                    for value in values:
                        sql_query = cls.get_searcher(search)(
                            cls, search, value, sql_query, query
                        )

            # TODO: Handle sorting

            # Handle pagination
            count = int(
                query.modifiers.get("_count", [settings.DEFAULT_BUNDLE_SIZE])[0]
            )
            count = min(count, settings.MAX_BUNDLE_SIZE)
            offset = query.search_params.get("search-offset", ["1"])
            offset = int(offset[0])
            page = offset // count + 1
            pagination = cls.paginate(sql_query, page, count)
            url_queries = "&".join(
                [
                    f"{param}={value}"
                    for param, values in query.search_params.items()
                    for value in values
                    if param != "search-offset"
                ]
            )
            url_queries = "&" + url_queries if url_queries else ""
            params = {
                "items": [
                    item.to_fhir(*args, query=query, **kwargs)
                    for item in pagination.items
                    if not hasattr(item, "audit_read")
                    or item.audit_read(query).outcome == AUDIT_SUCCESS
                ],
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_previous": pagination.has_previous,
                "next_page": f"{cls.__name__}/?_count={count}&search-offset={offset+count}{url_queries}",
                "previous_page": f"{cls.__name__}/?_count={count}&search-offset={max(offset-count,1)}{url_queries}",
            }
            return PaginatedBundle(pagination=params).as_json()

    @classmethod
    def has_searcher(cls, query_string):
        """
        Search if this resource has a registered searcher for the provided query string

        :param query_string: A query string that is matched against registered field names or regular expressions
                             by existing searchers
        :type query_string: string

        :returns: bool
        """
        for srch in cls.searchables():
            if re.match(srch, query_string):
                return True
        return False

    @classmethod
    def get_searcher(cls, query_string):
        """
        Return the first search function that matches the provided query string

        :param query_string: A query string that is matched against registered field names or regular expressions
                             by existing searchers
        :type query_string: string

        :returns: function
        """
        searchers = [
            func
            for srch, func in cls.searchables().items()
            if re.match(srch, query_string)
        ]
        if len(searchers) == 0:
            raise AttributeError(f"Searcher does not exist: {query_string}")
        return searchers[0]

    @classmethod
    def searchables(cls):
        """
        Returns a list od two-tuples containing the name of a searchable attribute and the function that searches for it based
        on the Attribute definitions in the FhirMap subclass.
        """
        searchables = {}
        for name, prop in cls.FhirMap.__dict__.items():
            if isinstance(prop, Attribute) and prop.searcher:
                key = name if not hasattr(prop, "search_regex") else prop.search_regex
                searchables[key] = prop.searcher
        return searchables

    @property
    def Fhir(self):
        """
        Wrapper property that initializes an instance of FhirMap.
        """
        # Initialize the FhirMap instance
        ## TODO: should we use a base class instead and implement __init__?
        if not hasattr(self, "_Fhir"):
            self._Fhir = self.FhirMap()
            self._Fhir._model = self
            self._Fhir._properties = [
                prop
                for prop, typ in self.FhirMap.__dict__.items()
                if isinstance(typ, Attribute)
            ]
            # self._Fhir._searchables = [(name, prop.searcher) for name, prop in self.FhirMap.__dict__.items() if name in self._Fhir._properties and prop.searcher]

        # Return the singleton
        return self._Fhir
