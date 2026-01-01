Exceptions
==========

.. automodule:: segmind.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

The exceptions module provides error handling classes for the Segmind SDK.

Error Handling
--------------

All API errors are wrapped in :class:`SegmindError` exceptions that provide structured information about what went wrong.

Error Attributes
----------------

:class:`SegmindError` provides the following attributes:

* :attr:`SegmindError.status` - HTTP status code
* :attr:`SegmindError.detail` - Error detail message
* :attr:`SegmindError.title` - Error title (optional)
