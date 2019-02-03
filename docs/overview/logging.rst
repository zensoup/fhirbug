Logging
-------

Fhirbug's :mod:`RequestHandlers <fhirbug.server.requesthandlers>` all have a
method called ``log_request`` that is called whenever a request is done being proccessed
with several information about the request.

By default, this method returns an :class:`AuditEvent <fhirbug.Fhir.Resources.auditevent.AuditEvent>` FHIR resource instance populated
with available information about the request.


Enhancing or persisting the default handler
___________________________________________________

Enhancing the generated AuditEvents with extra information about the request
and Persisiting them is pretty simple. Just use custom :mod:`RequestHandlers <fhirbug.server.requesthandlers>` and override the ``log_request`` method:

::

    from fhirbug.Fhir.resources import AuditEventEntity
    from fhirbug.config import import_models

    class EnhancedLoggingMixin:
        def log_request(self, *args, **kwargs):
            audit_event = super(EnhancedLoggingMixin, self).log_request(*args, **kwargs)

            context = kwargs["query"].context
            user = context.user
            # We populate the entity field with info about the user
            audit_event.entity = [
                AuditEventEntity({
                    "type": {"display": "Person"},
                    "name": user.username,
                    "description": user.userid,
                })
            ]
            return audit_event


    class PersistentLoggingMixin:
        def log_request(self, *args, **kwargs):
            audit_event = super(PersistentLoggingMixin, self).log_request(*args, **kwargs)
            models = import_models()
            AuditEvent = getattr(models, 'AuditEvent')
            audit_event_model = AuditEvent.create_from_resource(audit_event)
            return audit_event

    # Create the handler
    class CustomGetRequestHandler(
        PersistentLoggingMixin, EnhancedLoggingMixin, GetRequestHandler
    ):
        pass

.. note:: In order to have access to the user instance we assume you have passed
          a query context to the request handler's handle method containing
          the necessary info

.. note:: Note that the order in which we pass the mixins to the custom handler class
          is important. Python applies mixins from right to left, meaning
          ``PersistentLoggingMixin``'s ``super()`` method will call
          ``EnhancedLoggingMixin``'s ``log_request`` and ``EnhancedLoggingMixin``'s
          ``super()`` method will call ``GetRequestHandler``'s


          So, we expect the AuditEvent that is persisted by the
          ``PersistentLoggingMixin`` to contain information about the user because
          it is comes before ``EnhancedLoggingMixin`` in the class definition


Creating a custom log handler
___________________________________________________

If you don't want to use fhirbug's default log handling and want to implement
something your self, the process is pretty much the same. You implement your own
``log_request`` method and process the information that is passed to it by
fhirbug any way you want. Essentially the only difference with the examples above
is that you do not call ``super()`` inside your custom log function.

The signature of the ``log_request`` function is the following:

.. automethod:: fhirbug.server.requesthandlers.AbstractRequestHandler.log_request(self, url, query, status, method, resource=None, OperationOutcome=None, request_body=None, time=datetime.now())
    :noindex:

Here's an example where we use python's built-in logging module:

::

    from datetme import datetime
    from logging import getLogger

    logger = getLogger(__name__)

    class CustomGetRequestHandler(GetRequestHandler):
        def log_request(self, url, status, method, *args, **kwargs):
            logger.info("%s: %s %s %s" % (datetime.now(), method, url, status))
