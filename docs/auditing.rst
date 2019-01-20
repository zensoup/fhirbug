Auditing
==========

With Fhirbug you can audit requests on three levels:

    - **Request level**: Allow or disallow the specific operation on the specific
      resource, and

    - **Resource level**: Allow or disallow access to each individual resource and/or limit access to each of its attributes.

    - **Attribute level**: Allow or disallow access to each individual attribute for each resource.


.. warning:: The Auditing API is still undergoing heavy changes and is even more unstable than the rest of the project.
             Use it at your own risk!



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

In order to implement auditing at the resource level, give your mapper models one or more of the
methods ``audit_read``, ``audit_create``, ``audit_update``, ``audit_delete``.
The signature for these methods is the same as the one for request handlers we saw above.
They accept a single parameter holding a :class:`FhirRequestQuery <fhirbug.server.requestparser.FhirRequestQuery>` and
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

If you want more refined control over which attributes can be changed and displayed, during the
execution of one of the above ``audit_*`` methods, you can call ``self.protect_attributes(*attrs*)`` and /or
``self.hide_attributes(*attrs*)``.
In both cases, ``*attrs*`` should be an iterable that contains a list of attribute names that should be protected or hidden.

protect_attributes()
~~~~~~~~~~~~~~~~~~~~
The list of attributes passed to ``protect_attributes`` will be marked as protected for the duration of this request
and will not be allowed to change

hide_attributes()
~~~~~~~~~~~~~~~~~~~~
The list of attributes passed to ``hide_attributes`` will be marked as hidden for the current request.
This means that in case of a POST or PUT request they may be changed but they will not
be included in the response.

For example if we wanted to hide patient contact information from unauthorized users,
we could do the following:

::

    class Patient(FhirBaseModel):
        # Database field definitions go here

        def audit_read(self, query):
            if not is_authorized(query.context.user):
                self.hide_attributes(['contact'])
            return AuditEvent(outcome="0", strict=False)

        class FhirMap:
            # Fhirbug Attributes go here


Similarly, if we wanted to only prevent unauthorized users from changing the Identifiers
of Patients we would use ``protect_attributes``:

::

    class Patient(FhirBaseModel):
        # Database field definitions go here

        def audit_update(self, query):
            if not is_authorized(query.context.user):
                self.protect_attributes = ['identifier']
            return AuditEvent(outcome="0", strict=False)

        class FhirMap:
            # Fhirbug Attributes go here


Auditing at the attribute level
--------------------------------

When declaring attributes, you can provide a function to the ``audit_set`` and ``audit_get``
keyword arguments. The signature for these functions is the same, they accept
a single positional argument and should return ``True`` if access to the attribute
is allowed, or ``False`` otherwise.
