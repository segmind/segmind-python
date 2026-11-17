Webhooks
========

.. automodule:: segmind.webhooks
   :members:
   :undoc-members:
   :show-inheritance:

The webhooks module provides functionality for managing webhook endpoints that receive real-time notifications when events occur.

Webhook Operations
------------------

The webhooks module supports these operations:

* :meth:`Webhooks.get` - List all configured webhooks
* :meth:`Webhooks.add` - Create a new webhook endpoint
* :meth:`Webhooks.update` - Point a webhook at a new URL
* :meth:`Webhooks.delete` - Deactivate a webhook
* :meth:`Webhooks.logs` - List the deliveries made to a webhook
* :meth:`Webhooks.test` - Send a ``WEBHOOK_TEST`` delivery (1.5.0 and later)
* :meth:`Webhooks.resend` - Send a past delivery's payload again, by its ``id`` from ``logs()`` (1.5.0 and later)

``test`` and ``resend`` each send a real delivery to your endpoint, in the
background after the call returns. Read ``logs()`` to see how it answered.

Event Types
-----------

Webhooks can be configured to receive notifications for different event types:

* **PIXELFLOW** - Pixelflow completion events
* **GENERATION** - Generation completion events
