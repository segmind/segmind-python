# Segmind Python SDK

A Python client library for interacting with Segmind APIs, providing easy access to model inference, PixelFlows, webhooks, file uploads, and more.

## Installation

```bash
pip install segmind
```

## Quick Start

```python
from segmind import SegmindClient

# Initialize the client
client = SegmindClient(api_key="your_api_key_here")
# Or use environment variable SEGMIND_API_KEY
client = SegmindClient()

# Generate an image
response = client.run(
    "seedream-v3-text-to-image",
    prompt="A beautiful sunset over mountains",
    aspect_ratio="16:9"
)

# Save the image
with open("sunset.jpg", "wb") as f:
    f.write(response.content)
```

## Features

### 🎨 Model Inference
Run various AI models for text-to-image, music generation, text-to-speech, and more.

### 🔄 PixelFlows
Execute complex workflows with polling support for long-running tasks.

### 🪝 Webhooks
Manage webhooks for real-time notifications about your API usage.

### 📁 File Uploads
Upload images, audio, and video files with support for multiple formats.

### 📊 Usage Analytics
Track your API usage and generations with detailed filtering options.

### 🔍 Model Discovery
Browse available models and their capabilities.

## Core Components

- **SegmindClient**: Main client for API interactions
- **PixelFlows**: Workflow execution and management
- **Webhooks**: Webhook configuration and monitoring
- **Files**: Media file upload handling
- **Generations**: Usage analytics and history
- **Models**: Model discovery and information

## Supported Media Formats

**Images**: png, jpg, jpeg, gif, bmp, webp, svg, ico, tif, tiff, jfif, pjp, apng, svgz, heif, heic, xbm

**Audio**: mp3, aiff, wma, au

**Video**: mp4, avi, mov, mkv, wmv, flv, webm, mpeg, mpg

## Examples

### Text to Image
```python
response = client.run(
    "seedream-v3-text-to-image",
    prompt="A cyberpunk cityscape at night",
    aspect_ratio="16:9"
)
```

### PixelFlows
```python
result = client.pixelflows.run(
    workflow_id="your-workflow-id",
    data={"prompt": "Generate an infographic"},
    poll=True
)
```

### File Upload (Segmind Storage)
```python
# Upload a file to Segmind Storage
result = client.files.upload("path/to/image.png")
print(result["file_urls"][0])
# https://images.segmind.com/assets/...

# Batch upload multiple files
result = client.files.upload(["image1.png", "image2.jpg"])
for url in result["file_urls"]:
    print(url)
```

### Webhooks
```python
# Add a webhook
client.webhooks.add("https://your-endpoint.com", ["PIXELFLOW"])

# Get all webhooks
webhooks = client.webhooks.get()
```

## Documentation

For detailed examples and API reference, see [examples.md](examples.md).

## Requirements

- Python 3.8+
- httpx
- typing-extensions (for Python < 3.10)

## Error Handling

The SDK provides comprehensive error handling with detailed error messages:

```python
from segmind import SegmindClient
from segmind.exceptions import SegmindError

try:
    client = SegmindClient()
    response = client.run("invalid-model", prompt="test")
except SegmindError as e:
    print(f"API Error: {e.detail}")
    print(f"Status Code: {e.status}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- GitHub Issues: [Report bugs or request features](https://github.com/segmind/segmind-python)
- Documentation: [API Documentation](https://docs.segmind.com)
- Examples: See [examples.md](examples.md) for comprehensive usage examples
