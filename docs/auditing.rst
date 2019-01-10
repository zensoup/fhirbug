Auditing
==========

With Fhirbug you can audit requests on two levels:

    - **Request level**: Allow or disallow the specific operation on the specific
      resource, and

    - **Resource level**: Allow or disallow access to each individual resource and/or limit access to each of its attributes.


Auditing at the request level
------------------------------

All you need to do do in order to implement request-level auditing in Fhribug
is to provide the built-in :mod:`fhirbug.server.requesthandlers` with an extra
method called ``audit_request``.

This method should accept a single positional parameter, a :class:`FhirRequestQuery <fhirbug.server.requestparser.FhirRequestQuery>` and should return an
:class:`AuditEvent <fhirbug.Fhir.Resources.AuditEvent>`. If the outcome attribute
of the returned ``AuditEvent`` is "0" (the code for *"Success"*), the request
is processed normally.


::

    from fhirbug.server.requesthandlers import GetRequestHandler
    from fhirbug.Fhir.resources import AuditEvent

    class CustomGetRequestHandler(GetRequestHandler):
        def audit_request(self, query):
            return AuditEvent(outcome="0", strict=False)

*The simplest possible auditing handler, one that approves all requests.*

In any other case, the request fails with status code ``403``,
and returns an OperationOutcome resource containing the ``outcomeDesc`` of the ``AuditEvent``. This way you can return information about the reasons for failure.

::

    from fhirbug.server.requesthandlers import GetRequestHandler
    from fhirbug.Fhir.resources import AuditEvent

    class CustomGetRequestHandler(GetRequestHandler):
        def audit_request(self, query):
            if "_history" in query.modifiers:
                if is_authorized(query.context.user):
                    return AuditEvent(outcome="0", strict=False)
                else:
                    return AuditEvent(
                        outcome="8",
                        outcomeDesc="Unauthorized accounts can not access resource history.",
                        strict=False
                    )

.. note:: Notice how we passed ``strict=False`` to the AuditEvent constructor?
          That's because without it, it would not allow us to create an AuditEvent resource
          without filling in all its required fields.

          However, since we do not store it in this example and instead just use it to communicate
          with the rest of the application, there is no need to let it validate our resource.

Since Fhirbug does not care about your web server implementation, or your
authentication mechanism, you need to collect and provide the information neccessary for authenticationg the request to the ``audit_request`` method.

Fhirbug's suggestion is passing this information through the ``query.context`` object, by providing ``query_context`` when calling the request handler's ``handle`` method.



Auditing at the resource level
------------------------------

Controlling access to the entire resource
_________________________________________

In order to implement auditing at the resource level, give your mapper models a
method called ``audit_read``. The signature for this method is the same as the
one for request handlers we saw above. It accepts a single parameter holding a :class:`FhirRequestQuery <fhirbug.server.requestparser.FhirRequestQuery>` and
should return an :class:`AuditEvent <fhirbug.Fhir.Resources.AuditEvent>`, whose
``outcome`` should be ``"0"`` for success and anything else for failure.

::

    class Patient(FhirBaseModel):
        # Database field definitions go here

        def audit_read(self, query):
            return AuditEvent(outcome="0", strict=False)

        class FhirMap:
            # Fhirbug Attributes go here

Controlling access to specific attributes
_________________________________________

If you want more refined control over which attributes are displayed, during the
execution of ``audit_read`` you can set ``self._visible_fields`` and /or ``self._hidden_fields``.
Both should be an iterable that contains a list of attribute names that should be hidden or visible.

For example if we wanted to hide patient contact information from unauthorized users,
we could do the following:

::

    class Patient(FhirBaseModel):
        # Database field definitions go here

        def audit_read(self, query):
            if not is_authorized(query.context.user):
                self._hidden_fields = ['contact']
            return AuditEvent(outcome="0", strict=False)

        class FhirMap:
            # Fhirbug Attributes go here

            
Similarly, if we wanted to only display ``text`` and ``name`` to unauthorized users
we could use ``_visible_fields``:

::

    class Patient(FhirBaseModel):
        # Database field definitions go here

        def audit_read(self, query):
            if not is_authorized(query.context.user):
                self._visible_fields = ['text', 'name']
            return AuditEvent(outcome="0", strict=False)

        class FhirMap:
            # Fhirbug Attributes go here
