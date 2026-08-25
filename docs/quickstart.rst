Quickstart Guide
================

This guide will help you get started with the Segmind Python SDK in just a few minutes.

Installation
------------

Install the SDK using pip:

.. code-block:: bash

   pip install segmind

Authentication
--------------

You'll need an API key from Segmind. You can get one by:

1. Visiting `https://www.segmind.com/`
2. Creating an account or signing in
3. Going to your API keys section
4. Creating a new API key

Once you have your API key, you can use it in several ways:

**Option 1: Environment Variable (Recommended)**

.. code-block:: bash

   export SEGMIND_API_KEY="your_api_key_here"

**Option 2: Direct Initialization**

.. code-block:: python

   from segmind import SegmindClient

   client = SegmindClient(api_key="your_api_key_here")

**Option 3: .env File**

Create a `.env` file in your project root:

.. code-block:: text

   SEGMIND_API_KEY=your_api_key_here

Then load it:

.. code-block:: python

   from dotenv import load_dotenv
   load_dotenv()

   from segmind import SegmindClient
   client = SegmindClient()

Your First API Call
-------------------

Let's start with a simple text-to-image generation. ``segmind.run`` submits
the request, waits for it to complete, and returns a ``dict`` whose
``"output"`` field holds the generated media URL:

.. code-block:: python

   import segmind

   result = segmind.run(
       "seedream-4.5",
       prompt="A cute cat sitting on a windowsill",
       aspect_ratio="1:1"
   )

   print(result["output"])
   # https://images.segmind.com/generations/...jpeg

If you prefer a single blocking call that returns the raw bytes, use
``run_sync`` (returns an ``httpx.Response``):

.. code-block:: python

   import segmind

   response = segmind.run_sync(
       "seedream-4.5",
       prompt="A cute cat sitting on a windowsill",
       aspect_ratio="1:1"
   )

   with open("cat.jpg", "wb") as f:
       f.write(response.content)


Next Steps
----------

Now that you have the basics, explore:

* :doc:`examples` - Detailed examples for each service
* :doc:`api/index` - Complete API reference
* :doc:`contributing` - How to contribute to the project

Common Use Cases
----------------

**Text to Image**

.. code-block:: python

   result = segmind.run(
       "seedream-4.5",
       prompt="A futuristic city skyline at night",
       aspect_ratio="16:9"
   )
   print(result["output"])

**Video Generation** (long jobs: submit, then wait with a custom deadline)

.. code-block:: python

   job = segmind.submit_async("seedance-2.0", prompt="A sunset timelapse")
   result = job.wait(timeout=900)
   print(result["output"])

**Music Generation**

.. code-block:: python

   result = segmind.run(
       "ace-step-music",
       genres="electronic",
       output_seconds=30
   )
   print(result["output"])

**Text to Speech**

.. code-block:: python

   result = segmind.run(
       "myshell-tts",
       voice="michael",
       text="Hello, welcome to Segmind!",
       language="EN_NEWEST"
   )
   print(result["output"])

**LLM Chat**

.. code-block:: python

   reply = segmind.chat("gpt-5.5", prompt="What is artificial intelligence?")
   print(reply.text)

Need Help?
----------

If you run into issues:

1. Check the :doc:`api/index` for detailed parameter information
2. Look at the :doc:`examples` for working examples
3. Visit our `GitHub repository <https://github.com/segmind/segmind-python>`_ for issues and discussions
4. Contact support at `support@segmind.com`
