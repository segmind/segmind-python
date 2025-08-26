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
* :meth:`Webhooks.edit` - Modify existing webhook configuration
* :meth:`Webhooks.delete` - Deactivate a webhook
* :meth:`Webhooks.logs` - Retrieve webhook delivery logs

Event Types
-----------

Webhooks can be configured to receive notifications for different event types:

* **PIXELFLOW** - Pixelflow completion events
* **GENERATION** - Generation completion events
