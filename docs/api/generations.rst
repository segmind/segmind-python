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
* :meth:`Generations.history` - List requests (failures included) with cost and inputs
* :meth:`Generations.get` - Get one request by its ``request_id``

Filtering Options
-----------------

The :meth:`Generations.list` method supports several filtering options:

* **page** - Page number for pagination
* **model_name** - Filter by specific model
* **start_date** - Filter by start date (YYYY-MM-DD format)
* **end_date** - Filter by end date (YYYY-MM-DD format)
* **user_id** - Filter by the user who made the generation (UUID). Inside a team,
  any member of that team may be requested; otherwise only your own user id is
  accepted.

Generation Data
---------------

Each row returned by :meth:`Generations.list` contains:

* ``id``, ``request_id``, ``created_at``, ``updated_at``
* ``model_name`` and ``generation_url`` (the output)
* ``user_id`` and ``user_email``
* ``status`` - ``COMPLETED``, ``FAILED`` or ``PENDING``
* ``credits_deduction`` - what the request cost, in USD
* ``latency_ms``
* ``prompt`` and ``parameters`` - the inputs the request was made with

The last five come from the request record, which is written shortly after the
output, so a generation only seconds old may still have them as ``None``.
