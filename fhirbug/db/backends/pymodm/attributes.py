from bson.objectid import ObjectId
from bson.errors import InvalidId

from fhirbug.models.attributes import Attribute
from fhirbug.config import settings, import_models
from fhirbug.exceptions import MappingValidationError, DoesNotExistError


class ObjectIdReferenceAttribute(Attribute):
    """
    A Reference to some other Resource of one or
    more possible types that may be contained.

    Native pymodm references must explicitly specify the related model type,
    which doesn't work for us since we accept several possible types. This is
    why we use ObjectIds to store references.
    """

    def __init__(
        self,
        possible_types,
        pk_getter,
        name,
        pk_setter=None,
        force_display=False,
        searcher=None,
    ):
        self.possible_types = possible_types
        self.pk_getter = pk_getter
        self.setter = pk_setter
        self.name = name
        self.force_display = force_display
        self.searcher = searcher

    def __get__(self, instance, owner):
        models = import_models()
        classes = [getattr(models, cls_name) for cls_name in self.possible_types]
        pk = Attribute(self.pk_getter).__get__(instance, None)
        resource = None
        for cls in classes:
            if resource is None:
                try:
                    resource = cls._get_item_from_pk(pk)
                    cls_name = cls.__name__
                except:
                    pass
        if resource is None:
            return None

        if (
            self.name in instance._model._contained_names
        ):  # The resource should be contained
            # Get the item
            as_fhir = resource.to_fhir()

            instance._model._refcount += 1

            as_fhir.id = f"ref{instance._model._refcount}"
            instance._model._contained_items.append(as_fhir)

            # Build the reference dict
            reference = {"reference": f"#ref{instance._model._refcount}"}

            # Add a display if possible
            if hasattr(resource, "_as_display"):
                reference["display"] = resource._as_display

            return reference

        else:  # The resource is not contained, generate a url

            # Build the reference dict
            reference = {
                "reference": f"{cls_name}/{pk}",
                "identifier": {"system": f"{cls_name}", "value": str(pk)},
            }

            if self.force_display:  # Do a query to fetch the display
                # TODO: can we check if it supprts `_as_display` before querying?
                if hasattr(resource, "_as_display"):
                    reference["display"] = resource._as_display

            return reference

    def __set__(self, instance, reference):
        if not self.setter:
            return
        sys = value = None
        # First, we check to see if we have an identifier present
        # if hasattr(reference, "identifier"):
        #     # TODO: Handle Identifiers
        #     try:
        #         sys = reference.identifier.system
        #         value = reference.identifier.value
        #     except AttributeError:
        #         pass

        if hasattr(reference, "reference"):
            value = reference.reference
            if value is None or '/' not in value:
                raise MappingValidationError("Invalid subject")
            model_type, id = value.split('/')

        try:
            value = ObjectId(id)
        except InvalidId:
            raise MappingValidationError(f"{id} is an invalid resource identifier")

        models = import_models()
        model_cls = getattr(models, model_type, None)
        if model_type is None:
            raise MappingValidationError(f"Resource {model_type} does not exist.")
        try:
            resource = model_cls._get_item_from_pk(value)
        except DoesNotExistError as e:
            if settings.STRICT_MODE['set_non_existent_reference']:
                raise MappingValidationError(f"{e.resource_type}/{e.pk} was not found on the server.")
            else:
                print(f"{e.resource_type}/{e.pk} was not found on the server.")

        return super(ObjectIdReferenceAttribute, self).__set__(instance, value)
