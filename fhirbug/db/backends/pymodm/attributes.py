from bson.objectid import ObjectId

from fhirbug.models.attributes import Attribute
from fhirbug.config import import_models
from fhirbug.exceptions import MappingValidationError


class ReferenceAttribute(Attribute):
    """
    A Reference to some other Resource of one or
    more possible types that may be contained.
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
        if hasattr(reference, "identifier"):
            try:
                # TODO: can we make this all a user-defined parameter for the entire identifier?
                sys = reference.identifier.system
                # assigner = reference.identifier.assigner
                # if assigner == getattr(settings, 'ORGANIZATION_NAME', 'CSSA') and sys == 'Patient':
                value = reference.identifier.value
            except AttributeError:
                pass
        value = ObjectId(value)
        return super(ReferenceAttribute, self).__set__(instance, value)

        if hasattr(reference, "reference"):
            ref = reference.reference
            if ref.startswith("#"):
                # TODO read internal reference
                pass

        if value is None:
            raise MappingValidationError("Invalid subject")

        setattr(instance._model, self.id, value)
