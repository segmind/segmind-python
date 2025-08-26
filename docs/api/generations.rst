Generations
===========

.. automodule:: segmind.generations
   :members:
   :undoc-members:
   :show-inheritance:

The generations module provides functionality for retrieving and managing your generation history.

Generation Management
---------------------

The generations module supports these operations:

* :meth:`Generations.recent` - Get recent generations for a specific model
* :meth:`Generations.list` - List all generations with filtering and pagination

Filtering Options
-----------------

The :meth:`Generations.list` method supports several filtering options:

* **page** - Page number for pagination
* **model_name** - Filter by specific model
* **start_date** - Filter by start date (YYYY-MM-DD format)
* **end_date** - Filter by end date (YYYY-MM-DD format)

Generation Data
---------------

Each generation contains information about:

* Generation ID and timestamps
* Model used for generation
* Input parameters
* Output data and URLs
* Generation status and metadata
