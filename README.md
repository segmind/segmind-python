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

### File Upload

```python
result = client.files.upload("path/to/image.png")
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

## Development

### Running Tests

The project includes a comprehensive test suite. To run tests locally:

```bash
# Install development dependencies
pip install -e ".[test]"

# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=segmind --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Ensure code quality: `pre-commit run --all-files`
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- GitHub Issues: [Report bugs or request features](https://github.com/segmind/segmind-python)
- Documentation: [API Documentation](https://docs.segmind.com)
- Examples: See [examples.md](examples.md) for comprehensive usage examples
