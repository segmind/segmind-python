# Segmind Python SDK Examples

Usage examples for every module in the Segmind Python SDK.

The default way to run a model is `segmind.run(slug, **params)` — it submits to the
async v2 queue, polls until the job completes, and returns the result as a `dict`.
Use `segmind.run_sync` only when you specifically want a single blocking v1 call
that returns the raw `httpx.Response` bytes.

## Setup

Set your API key as an environment variable:

```bash
export SEGMIND_API_KEY="your_api_key_here"
```

The module-level functions (`segmind.run`, `segmind.chat`, …) use a default client
configured from the environment. Instantiate `SegmindClient` yourself only when you
need a custom timeout, base URL, or an explicit key:

```python
from segmind import SegmindClient

client = SegmindClient()                              # uses SEGMIND_API_KEY
client = SegmindClient(api_key="your_api_key_here")   # explicit key
client = SegmindClient(timeout=120)                   # custom HTTP timeout
```

## Run a Model

### Generate an Image from Text

`run` returns a `dict`; the generated media is a URL in `result["output"]`.

```python
import segmind

result = segmind.run(
    "seedream-4.5",
    prompt="A beautiful raining sunrise over dark fiery mountains",
    aspect_ratio="16:9",
)
print(result["output"])
# https://images.segmind.com/generations/...jpeg
```

### Generate a Video

Video models can run for several minutes. `run` waits up to 600 seconds by
default; use `submit_async` + `wait(timeout=...)` for a longer deadline.

```python
import segmind

job = segmind.submit_async(
    "seedance-2.0",
    prompt="A sailboat crossing a stormy sea, cinematic",
)
print(job.request_id)          # track or log the request
result = job.wait(timeout=900) # poll until COMPLETED, up to 15 minutes
print(result["output"])
```

### Generate Music

```python
import segmind

result = segmind.run(
    "ace-step-music",
    genres="jazz",
    output_seconds=30,
)
print(result["output"])
```

### Text to Speech

```python
import segmind

result = segmind.run(
    "myshell-tts",
    voice="michael",
    language="EN_NEWEST",
    text="Did you ever hear a folk tale about a giant turtle?",
    speed=1,
)
print(result["output"])
```

### Edit an Image with a Model

Pass input images as URLs — upload local files first (see Files below).

```python
import segmind

upload = segmind.files.upload("input_image.jpg")

result = segmind.run(
    "gpt-image-2",
    image=upload["file_urls"][0],
    prompt="Add a sunset background",
)
print(result["output"])
```

### Synchronous Call (raw bytes)

`run_sync` makes a single blocking v1 request and returns the raw
`httpx.Response` — the media bytes are in `response.content`. Best for fast
image models when you want the file directly instead of a URL.

```python
import segmind

response = segmind.run_sync(
    "seedream-4.5",
    prompt="A cyberpunk cityscape at night",
    aspect_ratio="16:9",
)

with open("image.jpg", "wb") as f:
    f.write(response.content)
```

### Track a Long-Running Job

`submit_async` returns an `AsyncJob` handle so you can poll on your own
schedule or run other work in between.

```python
import segmind

job = segmind.submit_async("seedance-2.0", prompt="A sunset timelapse")

print(job.request_id)
print(job.status())            # e.g. {"status": "PROCESSING", ...}

result = job.wait(timeout=900, interval=5)  # poll every 5s, 15 min deadline
print(result["output"])
```

## Error Handling

`run`, `run_sync`, and `chat` raise `SegmindError` for API errors. The async
path additionally raises `InferenceFailed` when the job reaches FAILED and
`InferenceTimeout` when `wait`'s deadline is exceeded (both are subclasses of
`SegmindError`).

```python
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
```

## LLM Chat

### Chat with a Language Model

`chat` is async by default (mirrors `run`). The returned `ChatResponse.text` is
normalized across OpenAI, Anthropic, and Gemini response shapes.

```python
import segmind

reply = segmind.chat("gpt-5.5", prompt="Write a haiku about the sea")
print(reply.text)
print(reply.usage, reply.finish_reason)
```

### Multi-Turn Conversation

```python
import segmind

messages = [
    {"role": "user", "content": "tell me a joke on cats"},
    {"role": "assistant", "content": "here is a joke about cats..."},
    {"role": "user", "content": "now a joke on dogs"},
]

reply = segmind.chat("claude-4.5-sonnet", messages=messages)
print(reply.text)
```

### Single Blocking Chat Call

```python
import segmind

reply = segmind.chat_sync("gpt-5.5", prompt="tell me a joke on cats")
print(reply.text)
```

### Chat About an Image (Multimodal)

`segmind.image_url()` inlines a local file as a base64 data-URI message part.

```python
import segmind

msg = {"role": "user", "content": [
    {"type": "text", "text": "Describe this image"},
    segmind.image_url("photo.jpg"),
]}
reply = segmind.chat("gpt-5.5", messages=[msg])
print(reply.text)
```

### Chat with a Job Handle

```python
import segmind

job = segmind.submit_chat("gpt-5.5", prompt="Summarize the plot of Dune")
print(job.request_id)
reply = job.wait(timeout=300)
print(reply.text)
```

## Files (Segmind Storage)

Upload files to Segmind Storage and receive persistent URLs that can be reused
across model runs and PixelFlow workflows.

### Upload a File

```python
import segmind

result = segmind.files.upload("path/to/image.png")
print(result)
# {'file_urls': ['https://images.segmind.com/assets/...'], 'message': 'Files uploaded successfully'}

file_url = result["file_urls"][0]
```

### Upload Multiple Files

```python
import segmind

result = segmind.files.upload([
    "path/to/image1.png",
    "path/to/image2.jpg",
    "path/to/image3.webp",
])

for url in result["file_urls"]:
    print(url)
```

### Supported Formats

- **Images**: png, jpg, jpeg, gif, bmp, webp, svg, ico, tif, tiff, jfif, pjp, apng, svgz, heif, heic, xbm
- **Audio**: mp3, aiff, wma, au
- **Video**: mp4, avi, mov, mkv, wmv, flv, webm, mpeg, mpg

## PixelFlows

### Run a Workflow

```python
import segmind

result = segmind.pixelflows.run(
    workflow_id="6839bf53659263e69c7a567a-v1",
    data={"Text_Prompt": "I am happy with this client's services"},
    poll=True,
)
print("Workflow result:", result)
```

### Run a Workflow with Uploaded Files

```python
import segmind

upload = segmind.files.upload(["image1.jpg", "image2.jpg"])
urls = upload["file_urls"]

result = segmind.pixelflows.run(
    workflow_id="your-workflow-id",
    data={"input_image_1": urls[0], "input_image_2": urls[1]},
    poll=True,
)
```

### Submit a Workflow Without Waiting

```python
import segmind

result = segmind.pixelflows.run(
    workflow_id="your_workflow_id",
    data={"input_param": "value"},
    poll=False,
)
poll_id = result.get("request_id")
print(f"Request submitted with ID: {poll_id}")
```

### Check Workflow Status

```python
import segmind

status = segmind.pixelflows.get_status(poll_id="4f7471d8ac431cffe0468dc487b5d354")
print(f"Current status: {status}")
```

### Poll a Workflow Until Done

```python
import segmind

result = segmind.pixelflows.poll(
    poll_id="4f7471d8ac431cffe0468dc487b5d354",
    poll_interval=3,
    max_wait_time=600,
)
print(f"Final result: {result}")
```

### Workflow Response Formats

```python
# The response shape depends on status:

# 1. QUEUED:
# {'message': '...', 'poll_url': '...', 'request_id': '...', 'status': 'QUEUED'}

# 2. PROCESSING:
# {'output': '', 'status': 'PROCESSING'}

# 3. COMPLETED:
# {'output': [{"keyname": "Infographic", "value": {"data": "image_url", "type": "image"}}], 'status': 'COMPLETED'}

# 4. FAILED:
# {'error_message': {...}, 'status': 'FAILED'}
```

## Webhooks

### Get All Webhooks

```python
import segmind

webhooks = segmind.webhooks.get()
print(webhooks)
```

### Add a Webhook

```python
import segmind

result = segmind.webhooks.add("https://your-endpoint.com", ["PIXELFLOW"])
print(result)
```

### Update a Webhook

```python
import segmind

result = segmind.webhooks.update(
    webhook_id="53a5fce9-11b7-4425-91da-47bd6515a8f9",
    webhook_url="https://newurl.com",
    event_types=["PIXELFLOW"],
)
```

### Delete a Webhook

```python
import segmind

result = segmind.webhooks.delete("53a5fce9-11b7-4425-91da-47bd6515a8f9")
```

### Get Webhook Logs

```python
import segmind

logs = segmind.webhooks.logs("53a5fce9-11b7-4425-91da-47bd6515a8f9")
print(logs)
```

## Models

### List All Models

```python
import segmind

models = segmind.models.list()
print(models)
```

## Generations

### Get Recent Generations for a Model

```python
import segmind

recent = segmind.generations.recent("seedream-4.5")
print(recent)
```

### List Generation History

```python
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
```

## Advanced Usage

For custom configuration (timeout, base URL, explicit API key), use
`SegmindClient` directly — it exposes the same methods and namespaces:

```python
from segmind import SegmindClient

client = SegmindClient(api_key="your_api_key", timeout=120.0)

result = client.run("seedream-4.5", prompt="A sunset")
response = client.run_sync("seedream-4.5", prompt="A sunset")

result = client.files.upload("image.png")
result = client.pixelflows.run(workflow_id="...", data={"prompt": "..."})
webhooks = client.webhooks.get()
```
