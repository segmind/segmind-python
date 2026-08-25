Examples
========

Usage examples for every module in the Segmind Python SDK.

The default way to run a model is ``segmind.run(slug, **params)`` — it submits
to the async v2 queue, polls until the job completes, and returns the result as
a ``dict``. Use ``segmind.run_sync`` only when you specifically want a single
blocking v1 call that returns the raw ``httpx.Response`` bytes.

.. _examples:client-setup:

Client Setup
------------

The module-level functions (``segmind.run``, ``segmind.chat``, …) use a default
client configured from the ``SEGMIND_API_KEY`` environment variable.
Instantiate ``SegmindClient`` only for custom configuration:

.. code-block:: python

   from segmind import SegmindClient

   client = SegmindClient()                              # uses SEGMIND_API_KEY
   client = SegmindClient(api_key="your_api_key_here")   # explicit key
   client = SegmindClient(timeout=120)                   # custom HTTP timeout

.. _examples:basic-model-inference:

Run a Model
-----------

Text to Image
~~~~~~~~~~~~~

``run`` returns a ``dict``; the generated media is a URL in ``result["output"]``.

.. code-block:: python

   import segmind

   result = segmind.run(
       "seedream-4.5",
       prompt="A beautiful raining sunrise over dark fiery mountains",
       aspect_ratio="16:9",
   )
   print(result["output"])
   # https://images.segmind.com/generations/...jpeg

Video Generation
~~~~~~~~~~~~~~~~

Video models can run for several minutes. ``run`` waits up to 600 seconds by
default; use ``submit_async`` + ``wait(timeout=...)`` for a longer deadline.

.. code-block:: python

   import segmind

   job = segmind.submit_async(
       "seedance-2.0",
       prompt="A sailboat crossing a stormy sea, cinematic",
   )
   result = job.wait(timeout=900)
   print(result["output"])

Music Generation
~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   result = segmind.run(
       "ace-step-music",
       genres="jazz",
       output_seconds=30,
   )
   print(result["output"])

Text-to-Speech
~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   result = segmind.run(
       "myshell-tts",
       voice="michael",
       language="EN_NEWEST",
       text="Did you ever hear a folk tale about a giant turtle?",
       speed=1,
   )
   print(result["output"])

Synchronous Call (raw bytes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``run_sync`` makes a single blocking v1 request and returns the raw
``httpx.Response`` — the media bytes are in ``response.content``.

.. code-block:: python

   import segmind

   response = segmind.run_sync(
       "seedream-4.5",
       prompt="A cyberpunk cityscape at night",
       aspect_ratio="16:9",
   )

   with open("image.jpg", "wb") as f:
       f.write(response.content)

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   import segmind
   from segmind import InferenceFailed, InferenceTimeout, SegmindError

   try:
       result = segmind.run("seedream-4.5", prompt="A sunset")
   except InferenceTimeout as e:
       print(f"Still running after deadline; request_id={e.request_id}")
   except InferenceFailed as e:
       print(f"Generation failed: {e.detail}")
   except SegmindError as e:
       print(f"API error {e.status}: {e.detail}")

.. _examples:llm-chat:

LLM Chat
--------

``chat`` is async by default (mirrors ``run``). The returned
``ChatResponse.text`` is normalized across OpenAI, Anthropic, and Gemini
response shapes.

.. code-block:: python

   import segmind

   reply = segmind.chat("gpt-5.5", prompt="Write a haiku about the sea")
   print(reply.text)
   print(reply.usage, reply.finish_reason)

   # Multi-turn conversation
   messages = [
       {"role": "user", "content": "tell me a joke on cats"},
       {"role": "assistant", "content": "here is a joke about cats..."},
       {"role": "user", "content": "now a joke on dogs"},
   ]
   reply = segmind.chat("claude-4.5-sonnet", messages=messages)

   # Single blocking call
   reply = segmind.chat_sync("gpt-5.5", prompt="tell me a joke")

   # Multimodal: inline a local image as a base64 data-URI
   msg = {"role": "user", "content": [
       {"type": "text", "text": "Describe this image"},
       segmind.image_url("photo.jpg"),
   ]}
   reply = segmind.chat("gpt-5.5", messages=[msg])

.. _examples:webhooks:

Webhooks
--------

Get All Webhooks
~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   webhooks = segmind.webhooks.get()
   print(webhooks)

Add a Webhook
~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   result = segmind.webhooks.add("https://your-endpoint.com", ["PIXELFLOW"])
   print(result)

Update a Webhook
~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   result = segmind.webhooks.update(
       webhook_id="53a5fce9-11b7-4425-91da-47bd6515a8f9",
       webhook_url="https://newurl.com",
       event_types=["PIXELFLOW"],
   )

Delete a Webhook
~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   result = segmind.webhooks.delete("53a5fce9-11b7-4425-91da-47bd6515a8f9")

Get Webhook Logs
~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   logs = segmind.webhooks.logs("53a5fce9-11b7-4425-91da-47bd6515a8f9")
   print(logs)

.. _examples:models:

Models
------

List All Models
~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   models = segmind.models.list()
   print(models)

.. _examples:files:

Files (Segmind Storage)
-----------------------

Upload files to Segmind Storage and receive persistent URLs that can be reused
across model runs and PixelFlow workflows.

.. code-block:: python

   import segmind

   # Single file
   result = segmind.files.upload("path/to/image.png")
   file_url = result["file_urls"][0]
   # https://images.segmind.com/assets/...

   # Multiple files
   result = segmind.files.upload(["image1.png", "image2.jpg"])
   for url in result["file_urls"]:
       print(url)

   # Use an uploaded file as model input
   result = segmind.run(
       "gpt-image-2",
       image=file_url,
       prompt="Add a sunset background",
   )

Supported formats:

* **Images**: png, jpg, jpeg, gif, bmp, webp, svg, ico, tif, tiff, jfif, pjp, apng, svgz, heif, heic, xbm
* **Audio**: mp3, aiff, wma, au
* **Video**: mp4, avi, mov, mkv, wmv, flv, webm, mpeg, mpg

.. _examples:generations:

Generations
-----------

Get Recent Generations
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   recent = segmind.generations.recent("seedream-4.5")
   print(recent)

List Generations
~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   all_generations = segmind.generations.list()          # page defaults to 1
   page_2 = segmind.generations.list(page=2)

   model_generations = segmind.generations.list(model_name="seedream-4.5")

   filtered = segmind.generations.list(
       page=1,
       model_name="gpt-image-2",
       start_date="2025-07-19",
       end_date="2025-08-19",
   )

.. _examples:pixelflows:

PixelFlows
----------

Run a Workflow
~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   # Run a workflow by ID with polling (waits for completion)
   result = segmind.pixelflows.run(
       workflow_id="6839bf53659263e69c7a567a-v1",
       data={"Text_Prompt": "I am happy with this client's services"},
       poll=True,
   )
   print("Workflow result:", result)

   # Submit without polling (returns immediately)
   result = segmind.pixelflows.run(
       workflow_id="your_workflow_id",
       data={"input_param": "value"},
       poll=False,
   )
   poll_id = result.get("request_id")

   # Custom polling settings
   result = segmind.pixelflows.run(
       workflow_id="your_workflow_id",
       data={"input_param": "value"},
       poll=True,
       poll_interval=5,
       max_wait_time=600,
   )

Get Workflow Status
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   status = segmind.pixelflows.get_status(poll_id="4f7471d8ac431cffe0468dc487b5d354")
   print(f"Current status: {status}")

Poll for Results
~~~~~~~~~~~~~~~~

.. code-block:: python

   import segmind

   result = segmind.pixelflows.poll(
       poll_id="4f7471d8ac431cffe0468dc487b5d354",
       poll_interval=3,
       max_wait_time=600,
   )
   print(f"Final result: {result}")

Response Formats
~~~~~~~~~~~~~~~~

.. code-block:: python

   # The response shape depends on status:

   # 1. QUEUED:
   # {'message': '...', 'poll_url': '...', 'request_id': '...', 'status': 'QUEUED'}

   # 2. PROCESSING:
   # {'output': '', 'status': 'PROCESSING'}

   # 3. COMPLETED:
   # {'output': [{"keyname": "Infographic", "value": {"data": "image_url", "type": "image"}}], 'status': 'COMPLETED'}

   # 4. FAILED:
   # {'error_message': {...}, 'status': 'FAILED'}
