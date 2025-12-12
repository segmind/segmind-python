Client
======

.. automodule:: segmind.client
   :members:
   :undoc-members:
   :show-inheritance:

The :class:`SegmindClient` is the main entry point for interacting with the Segmind API. It provides access to all service modules and handles authentication, HTTP client configuration, and basic model inference.

Service Access
--------------

The client provides access to various services through properties:

* :attr:`SegmindClient.pixelflows` - PixelFlow workflow management
* :attr:`SegmindClient.webhooks` - Webhook configuration
* :attr:`SegmindClient.models` - Model discovery
* :attr:`SegmindClient.files` - File upload operations
* :attr:`SegmindClient.generations` - Generation history
* :attr:`SegmindClient.accounts` - Account information
