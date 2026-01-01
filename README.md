# Segmind Python SDK

A Python client library for interacting with Segmind APIs, providing easy access to model inference, PixelFlows, webhooks, file uploads, and more.

## Installation

```bash
pip install segmind
```

## Quick Start

```python
import segmind

# Generate an image
response = segmind.run(
    "seedream-v3-text-to-image",
    prompt="A beautiful sunset over mountains",
    aspect_ratio="16:9"
)

# Save the image
with open("sunset2.jpg", "wb") as f:
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
import segmind

response = segmind.run(
    "seedream-v3-text-to-image",
    prompt="A cyberpunk cityscape at night",
    aspect_ratio="16:9"
)

with open("image.jpg", "wb") as f:
    f.write(response.content)
```

### PixelFlows

```python
import segmind

result = segmind.pixelflows.run(
    workflow_id="your-workflow-id",
    data={"prompt": "Generate an infographic"},
    poll=True
)
```

### File Upload

```python
import segmind

# Upload a file to Segmind Storage
result = segmind.files.upload("path/to/image.png")
print(result["file_urls"][0])
# https://images.segmind.com/assets/...

# Batch upload multiple files
result = segmind.files.upload(["image1.png", "image2.jpg"])
for url in result["file_urls"]:
    print(url)
```

### Webhooks

```python
import segmind

# Add a webhook
segmind.webhooks.add("https://your-endpoint.com", ["PIXELFLOW"])

# Get all webhooks
webhooks = segmind.webhooks.get()
```

### Finetuning
```python
# Get a presigned URL to upload your dataset (.zip)
upload = client.finetune.upload_presigned_url(name="my-dataset.zip")
# upload["presigned_url"] can be used with a PUT request to S3

# Submit a fine-tune request
job = client.finetune.submit(
    name="flux-job-1",
    data_source_path=upload["s3_url"],  # or any public zip URL
    instance_prompt="1MAN, running in brown suit",
    trigger_word="1MAN",
    base_model="FLUX",
    train_type="LORA",
    machine_type="NVIDIA_A100_40GB",
    theme="FLUX",
    segmind_public=False,
    advance_parameters={
        "steps": 1000,
        "batch_size": 2,
        "learning_rate": 4e-4,
    },
)

# Get details
details = client.finetune.details(request_id=job["finetune_id"])

# List all
all_jobs = client.finetune.list()

# Update access (public/private)
client.finetune.access_update(request_id=job["finetune_id"], segmind_public=True)

# Download model file (returns a temporary URL string)
download_url = client.finetune.file_download(cloud_storage_url=details["finetune"]["cloud_storage_url"])
```

## Documentation

For detailed examples and API reference, see [examples.md](examples.md).

Public API Playground (Swagger UI): open `docs/swagger.html` after building docs, or serve `docs/` statically. It loads the spec at `docs/_static/openapi/segmind-sdk.yaml` and supports the Authorize flow with `x-api-key`.

Run this to serve the documentation.
```python
python3 -m http.server 8000
```

## Requirements

- Python 3.8+
- httpx
- typing-extensions (for Python < 3.10)

## Error Handling

The SDK provides comprehensive error handling with detailed error messages:

```python
import segmind
from segmind.exceptions import SegmindError

try:
    response = segmind.run("invalid-model", prompt="test")
except SegmindError as e:
    print(f"API Error: {e.detail}")
    print(f"Status Code: {e.status}")
```

## Development

### Setup Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/segmind/segmind-python-internal.git
   cd segmind-python-internal
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[test,dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run verbose
make test-verbose
```

### Linting and Formatting

```bash
# Run all pre-commit checks
make lint

# Or run pre-commit directly
pre-commit run --all-files
```

### Building the Package

```bash
# Build distribution packages
make build

# Build and check with twine
make build-check
```

### Releasing

For information on creating releases and publishing to PyPI, see [RELEASING.md](RELEASING.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Ensure code quality: `pre-commit run --all-files`
6. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- GitHub Issues: [Report bugs or request features](https://github.com/segmind/segmind-python)
- Documentation: [API Documentation](https://docs.segmind.com)
- Examples: See [examples.md](examples.md) for comprehensive usage examples
