Models
======

.. automodule:: segmind.models
   :members:
   :undoc-members:
   :show-inheritance:

The models module provides functionality for discovering and getting information about available AI models.

Model Discovery
---------------

The :meth:`Models.get` method returns a list of all available models with their metadata, including:

* Model name and identifier
* Model type (text-to-image, text-to-speech, etc.)
* Input/output schemas
* Supported parameters
* Usage examples
