PixelFlows
==========

.. automodule:: segmind.pixelflows
   :members:
   :undoc-members:
   :show-inheritance:

The PixelFlows module provides functionality for running and managing complex AI workflows that combine multiple models and operations.

Pixelflow Management
--------------------

PixelFlows support several operations:

* :meth:`PixelFlows.run` - Execute pixelflows with optional polling
* :meth:`PixelFlows.get_status` - Check pixelflow status
* :meth:`PixelFlows.poll` - Poll for pixelflow completion

Response Formats
----------------

Pixelflows return different response formats based on their status:

* **QUEUED** - Pixelflow has been queued for execution
* **PROCESSING** - Pixelflow is currently running
* **COMPLETED** - Pixelflow completed successfully
* **FAILED** - Pixelflow failed with error details
