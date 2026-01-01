Examples
========

This document provides usage examples for all the modules in the Segmind Python SDK.

.. _examples:client-setup:

Client Setup
------------

.. code-block:: python

   from segmind import SegmindClient

   # Initialize the client
   client = SegmindClient(api_key="your_api_key_here")
   # Or use environment variable SEGMIND_API_KEY
   client = SegmindClient()

   # Initialize with custom timeout
   client = SegmindClient(timeout=120)

.. _examples:basic-model-inference:

Basic Model Inference
---------------------

Text to Image
~~~~~~~~~~~~~

.. code-block:: python

   # Generate an image from text
   response = client.run(
       "seedream-v3-text-to-image",
       prompt="A beautiful raining sunrise over dark fiery mountains",
       aspect_ratio="16:9",
   )

   # Save the image
   with open("sunrise.jpg", "wb") as f:
       f.write(response.content)

Music Generation
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Generate music
   response = client.run(
       "ace-step-music",
       genres="jazz",
       output_seconds=30,
   )

   # Save the audio
   with open("music.mp3", "wb") as f:
       f.write(response.content)

Text-to-Speech
~~~~~~~~~~~~~~~

.. code-block:: python

   # Convert text to speech
   input_data = {
       "voice": "michael",
       "language": "EN_NEWEST",
       "text": "Did you ever hear a folk tale about a giant turtle?",
       "speed": 1,
   }
   response = client.run("myshell-tts", **input_data)

   # Save the audio
   with open("tts.mp3", "wb") as f:
       f.write(response.content)

LLM Chat
~~~~~~~~

.. code-block:: python

   # Chat with a language model
   messages = [
       {"role": "user", "content": "tell me a joke on cats"},
       {"role": "assistant", "content": "here is a joke about cats..."},
       {"role": "user", "content": "now a joke on dogs"},
   ]

   response = client.run("qwen2p5-vl-32b-instruct", messages=messages)
   print(response.content)

.. _examples:webhooks:

Webhooks
--------

Get All Webhooks
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get all webhooks
   webhooks = client.webhooks.get()
   print(webhooks)

Add a Webhook
~~~~~~~~~~~~~

.. code-block:: python

   # Add a new webhook with default event types
   result = client.webhooks.add("https://omkarkabde.com", ["PIXELFLOW"])
   print(result)

Edit a Webhook
~~~~~~~~~~~~~~

.. code-block:: python

   # Edit an existing webhook
   result = client.webhooks.edit(
       webhook_id="53a5fce9-11b7-4425-91da-47bd6515a8f9",
       webhook_url="https://newurl.com",
       event_types=["PIXELFLOW"]
   )
   print(result)

Delete a Webhook
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Delete (deactivate) a webhook
   result = client.webhooks.delete("53a5fce9-11b7-4425-91da-47bd6515a8f9")
   print(result)

Get Webhook Logs
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get dispatch logs for a webhook
   logs = client.webhooks.logs("53a5fce9-11b7-4425-91da-47bd6515a8f9")
   print(logs)

.. _examples:models:

Models
------

Get All Models
~~~~~~~~~~~~~~

.. code-block:: python

   # Get all available models
   models = client.models.get()
   print(models)

.. _examples:files:

Files
-----

Upload Media Files
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Upload image files
   result = client.files.upload("path/to/image.png")
   result = client.files.upload("path/to/photo.jpg")
   result = client.files.upload("path/to/graphic.webp")
   result = client.files.upload("path/to/icon.svg")
   result = client.files.upload("path/to/photo.heic")

   # Upload audio files
   result = client.files.upload("path/to/music.mp3")
   result = client.files.upload("path/to/sound.aiff")
   result = client.files.upload("path/to/audio.wma")

   # Upload video files
   result = client.files.upload("path/to/video.mp4")
   result = client.files.upload("path/to/movie.avi")
   result = client.files.upload("path/to/clip.webm")

   # Supported formats:
   # Images: png, jpg, jpeg, gif, bmp, webp, svg, ico, tif, tiff, jfif, pjp, apng, svgz, heif, heic, xbm
   # Audio: mp3, aiff, wma, au
   # Video: mp4, avi, mov, mkv, wmv, flv, webm, mpeg, mpg

.. _examples:generations:

Generations
-----------

Get Recent Generations
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get recent generations for a specific model (model_name required)
   recent = client.generations.recent("seededit-v3")
   print(recent)

List Generations
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get all generations (page defaults to 1)
   all_generations = client.generations.list()
   print(all_generations)

   # Get generations with pagination
   page_2 = client.generations.list(page=2)
   print(page_2)

   # Get generations filtered by model
   model_generations = client.generations.list(model_name="seededit-v3")
   print(model_generations)

   # Get generations with date range filter
   filtered_generations = client.generations.list(
       page=1,
       model_name="seededit-v3",
       start_date="2025-07-19",
       end_date="2025-08-19"
   )
   print(filtered_generations)

.. _examples:pixelflows:

PixelFlows
----------

Run a Workflow
~~~~~~~~~~~~~~

.. code-block:: python

   # Example 1: Run a workflow by ID with polling
   workflow_id = "6839bf53659263e69c7a567a-v1"
   data = {"Text_Prompt": "I am happy with this client's services"}

   result = client.pixelflows.run(
       workflow_id=workflow_id,
       data=data,
       poll=True  # Wait for completion
   )
   print("Workflow result:", result)

   # Example 2: Run a workflow by URL
   workflow_url = "https://api.segmind.com/workflows/6839bf53659263e69c7a567a-v1"
   result = client.pixelflows.run(
       workflow_url=workflow_url,
       data=data,
       poll=True
   )
   print("Workflow result:", result)

   # Example 3: Submit without polling and handle manually
   result = client.pixelflows.run(
       workflow_id=workflow_id,
       data=data,
       poll=False  # Don't wait, return immediately
   )

   poll_id = result.get("request_id")
   print(f"Request submitted with ID: {poll_id}")

   # Custom polling settings
   result = client.pixelflows.run(
       workflow_id="your_workflow_id",
       data={"input_param": "value"},
       poll=True,
       poll_interval=5,  # Poll every 5 seconds
       max_wait_time=600  # Wait up to 10 minutes
   )
   print(result)

Get Workflow Status
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Check status by poll ID (returned as request_id from API)
   status = client.pixelflows.get_status(poll_id="4f7471d8ac431cffe0468dc487b5d354")
   print(f"Current status: {status}")

   # Check status by poll URL
   poll_url = "https://api.segmind.com/workflows/request/4f7471d8ac431cffe0468dc487b5d354"
   status = client.pixelflows.get_status(poll_url=poll_url)
   print(f"Status from poll URL: {status}")

Poll for Results
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Poll an existing request using poll_id
   result = client.pixelflows.poll(
       poll_id="4f7471d8ac431cffe0468dc487b5d354",
       poll_interval=3,
       max_wait_time=600
   )
   print(f"Final result: {result}")

   # Poll for results by poll URL
   result = client.pixelflows.poll(
       poll_url="https://api.segmind.com/workflows/request/your_poll_id",
       poll_interval=3,
       max_wait_time=600
   )
   print(result)

Response Formats
~~~~~~~~~~~~~~~~

.. code-block:: python

   # The response will have different formats based on status:

   # 1. QUEUED:
   # {'message': '...', 'poll_url': '...', 'request_id': '...', 'status': 'QUEUED'}

   # 2. PROCESSING:
   # {'output': '', 'status': 'PROCESSING'}

   # 3. COMPLETED:
   # {'output': [{"keyname": "Infographic", "value": {"data": "image_url", "type": "image"}}], 'status': 'COMPLETED'}

   # 4. FAILED:
   # {'error_message': {...}, 'status': 'FAILED'}
