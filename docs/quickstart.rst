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

Let's start with a simple text-to-image generation:

.. code-block:: python

   from segmind import SegmindClient

   # Initialize the client
   client = SegmindClient()

   # Generate an image
   response = client.run(
       "seedream-v3-text-to-image",
       prompt="A cute cat sitting on a windowsill",
       aspect_ratio="1:1"
   )

   # Save the generated image
   with open("cat.jpg", "wb") as f:
       f.write(response.content)

   print("Image saved as cat.jpg!")


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

   response = client.run(
       "seedream-v3-text-to-image",
       prompt="A futuristic city skyline at night",
       aspect_ratio="16:9"
   )

**Music Generation**
.. code-block:: python

   response = client.run(
       "ace-step-music",
       genres="electronic",
       output_seconds=30
   )

**Text to Speech**
.. code-block:: python

   response = client.run(
       "myshell-tts",
       voice="michael",
       text="Hello, welcome to Segmind!",
       language="EN_NEWEST"
   )

**LLM Chat**
.. code-block:: python

   messages = [
       {"role": "user", "content": "What is artificial intelligence?"}
   ]

   response = client.run("qwen2p5-vl-32b-instruct", messages=messages)
   print(response.text)

Need Help?
----------

If you run into issues:

1. Check the :doc:`api/index` for detailed parameter information
2. Look at the :doc:`examples` for working examples
3. Visit our `GitHub repository <https://github.com/segmind/segmind>`_ for issues and discussions
4. Contact support at `support@segmind.com`
