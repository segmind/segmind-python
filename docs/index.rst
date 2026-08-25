Welcome to Segmind Python SDK Documentation
===========================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   quickstart
   examples
   api/index
   contributing

.. image:: https://img.shields.io/pypi/v/segmind.svg
   :target: https://pypi.org/project/segmind/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/segmind.svg
   :target: https://pypi.org/project/segmind/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/segmind/segmind-python.svg
   :target: https://github.com/segmind/segmind-python/blob/main/LICENSE
   :alt: License

The Segmind Python SDK provides a simple and intuitive interface to interact with Segmind's AI models and services. With this SDK, you can:

* Generate images from text descriptions
* Create music and audio content
* Convert text to speech
* Chat with language models
* Run complex workflows with PixelFlows
* Manage webhooks and file uploads
* And much more!

Quick Start
-----------

.. code-block:: python

   import segmind  # reads SEGMIND_API_KEY from the environment

   # Run a model (async v2 by default — submit + poll until done)
   result = segmind.run(
       "seedream-4.5",
       prompt="A beautiful sunset over mountains",
       aspect_ratio="16:9"
   )
   print(result["output"])
   # https://images.segmind.com/generations/...jpeg

Installation
------------

.. code-block:: bash

   pip install segmind

For more information, see the :doc:`quickstart` guide.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
