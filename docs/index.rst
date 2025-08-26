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

.. image:: https://img.shields.io/github/license/segmind/segmind.svg
   :target: https://github.com/segmind/segmind/blob/main/LICENSE
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

   from segmind import SegmindClient

   # Initialize the client
   client = SegmindClient(api_key="your_api_key_here")

   # Generate an image
   response = client.run(
       "seedream-v3-text-to-image",
       prompt="A beautiful sunset over mountains",
       aspect_ratio="16:9"
   )

   # Save the result
   with open("sunset.jpg", "wb") as f:
       f.write(response.content)

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
