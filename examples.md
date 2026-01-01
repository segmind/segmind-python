# Segmind Python SDK Examples

This document provides usage examples for all the modules in the Segmind Python SDK.

## Setup

Set your API key as an environment variable:
```bash
export SEGMIND_API_KEY="your_api_key_here"
```

```python
from segmind import SegmindClient

# Initialize the client
client = SegmindClient(api_key="your_api_key_here")
# Or use environment variable SEGMIND_API_KEY
client = SegmindClient()

# Initialize with custom timeout
client = SegmindClient(timeout=120)
```

## Basic Model Inference

### Text to Image
```python
import segmind

# Generate an image from text
response = segmind.run(
    "seedream-v3-text-to-image",
    prompt="A beautiful raining sunrise over dark fiery mountains",
    aspect_ratio="16:9",
)

# Save the image
with open("sunrise.jpg", "wb") as f:
    f.write(response.content)
```

### Music Generation
```python
import segmind

# Generate music
response = segmind.run(
    "ace-step-music",
    genres="jazz",
    output_seconds=30,
)

# Save the audio
with open("music.mp3", "wb") as f:
    f.write(response.content)
```

### Text-to-Speech
```python
import segmind

# Convert text to speech
response = segmind.run(
    "myshell-tts",
    voice="michael",
    language="EN_NEWEST",
    text="Did you ever hear a folk tale about a giant turtle?",
    speed=1,
)

# Save the audio
with open("tts.mp3", "wb") as f:
    f.write(response.content)
```

### LLM Chat
```python
import segmind

# Chat with a language model
messages = [
    {"role": "user", "content": "tell me a joke on cats"},
    {"role": "assistant", "content": "here is a joke about cats..."},
    {"role": "user", "content": "now a joke on dogs"},
]

response = segmind.run("qwen2p5-vl-32b-instruct", messages=messages)
print(response.content)
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
    event_types=["PIXELFLOW"]
)
print(result)
```

### Delete a Webhook
```python
import segmind

result = segmind.webhooks.delete("53a5fce9-11b7-4425-91da-47bd6515a8f9")
print(result)
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

## Files (Segmind Storage)

Upload files to Segmind Storage and receive persistent URLs that can be reused across multiple model runs and PixelFlow workflows.

### Single File Upload
```python
import segmind

result = segmind.files.upload("path/to/image.png")
print(result)
# {'file_urls': ['https://images.segmind.com/assets/...'], 'message': 'Files uploaded successfully'}

# Access the uploaded file URL
file_url = result["file_urls"][0]
print(file_url)
```

### Batch Upload (Multiple Files)
```python
import segmind

result = segmind.files.upload([
    "path/to/image1.png",
    "path/to/image2.jpg",
    "path/to/image3.webp"
])

# Access individual URLs
for url in result["file_urls"]:
    print(url)
```

### Using Uploaded Files with Models
```python
import segmind

# Upload an image and use it with a model
upload_result = segmind.files.upload("input_image.jpg")
image_url = upload_result["file_urls"][0]

# Use the URL in a model request
response = segmind.run(
    "seededit-v3",
    image=image_url,
    prompt="Add a sunset background"
)
```

### Using with PixelFlows
```python
import segmind

# Upload files for use in a workflow
upload_result = segmind.files.upload(["image1.jpg", "image2.jpg"])
image_urls = upload_result["file_urls"]

# Use uploaded URLs in PixelFlow
result = segmind.pixelflows.run(
    workflow_id="your-workflow-id",
    data={
        "input_image_1": image_urls[0],
        "input_image_2": image_urls[1]
    },
    poll=True
)
```

### Supported Formats
- **Images**: png, jpg, jpeg, gif, bmp, webp, svg, ico, tif, tiff, jfif, pjp, apng, svgz, heif, heic, xbm
- **Audio**: mp3, aiff, wma, au
- **Video**: mp4, avi, mov, mkv, wmv, flv, webm, mpeg, mpg

## Generations

### Get Recent Generations
```python
import segmind

recent = segmind.generations.recent("seededit-v3")
print(recent)
```

### List Generations
```python
import segmind

# Get all generations (page defaults to 1)
all_generations = segmind.generations.list()
print(all_generations)

# Get generations with pagination
page_2 = segmind.generations.list(page=2)

# Get generations filtered by model
model_generations = segmind.generations.list(model_name="seededit-v3")

# Get generations with date range filter
filtered_generations = segmind.generations.list(
    page=1,
    model_name="seededit-v3",
    start_date="2025-07-19",
    end_date="2025-08-19"
)
```

## PixelFlows

### Run a Workflow
```python
import segmind

# Run a workflow by ID with polling (waits for completion)
result = segmind.pixelflows.run(
    workflow_id="6839bf53659263e69c7a567a-v1",
    data={"Text_Prompt": "I am happy with this client's services"},
    poll=True
)
print("Workflow result:", result)

# Run a workflow by URL
result = segmind.pixelflows.run(
    workflow_url="https://api.segmind.com/workflows/6839bf53659263e69c7a567a-v1",
    data={"prompt": "Generate an image"},
    poll=True
)

# Submit without polling (returns immediately)
result = segmind.pixelflows.run(
    workflow_id="your_workflow_id",
    data={"input_param": "value"},
    poll=False
)
poll_id = result.get("request_id")
print(f"Request submitted with ID: {poll_id}")

# Custom polling settings
result = segmind.pixelflows.run(
    workflow_id="your_workflow_id",
    data={"input_param": "value"},
    poll=True,
    poll_interval=5,  # Poll every 5 seconds
    max_wait_time=600  # Wait up to 10 minutes
)
```

### Get Workflow Status
```python
import segmind

# Check status by poll ID
status = segmind.pixelflows.get_status(poll_id="4f7471d8ac431cffe0468dc487b5d354")
print(f"Current status: {status}")

# Check status by poll URL
status = segmind.pixelflows.get_status(
    poll_url="https://api.segmind.com/workflows/request/4f7471d8ac431cffe0468dc487b5d354"
)
```

### Poll for Results
```python
import segmind

# Poll an existing request until completion
result = segmind.pixelflows.poll(
    poll_id="4f7471d8ac431cffe0468dc487b5d354",
    poll_interval=3,
    max_wait_time=600
)
print(f"Final result: {result}")
```

### Response Formats

```python
# The response will have different formats based on status:

# 1. QUEUED:
# {'message': '...', 'poll_url': '...', 'request_id': '...', 'status': 'QUEUED'}

# 2. PROCESSING:
# {'output': '', 'status': 'PROCESSING'}

# 3. COMPLETED:
# {'output': [{"keyname": "Infographic", "value": {"data": "image_url", "type": "image"}}], 'status': 'COMPLETED'}

# 4. FAILED:
# {'error_message': {...}, 'status': 'FAILED'}
```

## Advanced Usage

For custom configuration (timeout, base URL, explicit API key), use `SegmindClient` directly:

```python
from segmind import SegmindClient

# Custom client with longer timeout
client = SegmindClient(api_key="your_api_key", timeout=120.0)

# Run model
response = client.run("seedream-v3-text-to-image", prompt="A sunset")

# Access namespaces
result = client.files.upload("image.png")
result = client.pixelflows.run(workflow_id="...", data={...})
webhooks = client.webhooks.get()
```
