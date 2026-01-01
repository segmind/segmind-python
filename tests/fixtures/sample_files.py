"""Sample files and file-related fixtures for testing."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_image_png() -> Generator[Path, None, None]:
    """Create a temporary PNG image file for testing."""
    # Minimal valid PNG file (1x1 pixel transparent PNG)
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(png_data)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_image_jpg() -> Generator[Path, None, None]:
    """Create a temporary JPEG image file for testing."""
    # Minimal valid JPEG file
    jpeg_data = (
        b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H'
        b'\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08'
        b'\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19'
        b'\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' 
        b'",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11'
        b'\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03'
        b'\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4'
        b'\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01'
        b'\x00\x00?\x00\xaa\xff\xd9'
    )
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        f.write(jpeg_data)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_image_gif() -> Generator[Path, None, None]:
    """Create a temporary GIF image file for testing."""
    # Minimal valid GIF file (1x1 pixel)
    gif_data = (
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
        b'\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,'
        b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
        b'\x04\x01\x00;'
    )
    
    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as f:
        f.write(gif_data)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_audio_mp3() -> Generator[Path, None, None]:
    """Create a temporary MP3 audio file for testing."""
    # Minimal MP3 header
    mp3_data = (
        b'\xff\xfb\x90\x00\x00\x03\x48\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    )
    
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        f.write(mp3_data)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_audio_wav() -> Generator[Path, None, None]:
    """Create a temporary WAV audio file for testing."""
    # Minimal WAV file header
    wav_data = (
        b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00'
        b'\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00'
        b'data\x00\x00\x00\x00'
    )
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(wav_data)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_video_mp4() -> Generator[Path, None, None]:
    """Create a temporary MP4 video file for testing."""
    # Minimal MP4 file header
    mp4_data = (
        b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
        b'\x00\x00\x00\x08free\x00\x00\x00\x28mdat'
    )
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        f.write(mp4_data)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_video_avi() -> Generator[Path, None, None]:
    """Create a temporary AVI video file for testing."""
    # Minimal AVI file header
    avi_data = (
        b'RIFF\x00\x00\x00\x00AVI LIST\x00\x00\x00\x00hdrlavih'
        b'\x38\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00'
    )
    
    with tempfile.NamedTemporaryFile(suffix='.avi', delete=False) as f:
        f.write(avi_data)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_unsupported_file() -> Generator[Path, None, None]:
    """Create a temporary unsupported file type for testing."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        f.write(b'This is a text file, not supported for upload')
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_large_image() -> Generator[Path, None, None]:
    """Create a temporary large image file for testing."""
    # Create a larger PNG file (approximately 100KB)
    png_header = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00'
        b'\x00\x00\x01\x00\x08\x06\x00\x00\x00\x5c\x72\xa8\x66'
    )
    
    # Create image data chunk
    image_data = b'\x00' * 100000  # 100KB of zeros
    idat_chunk = b'IDAT' + len(image_data).to_bytes(4, 'big') + image_data
    
    # PNG end chunk
    png_end = b'\x00\x00\x00\x00IEND\xaeB`\x82'
    
    full_png = png_header + idat_chunk + png_end
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(full_png)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_empty_file() -> Generator[Path, None, None]:
    """Create a temporary empty file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        # Write nothing to create an empty file
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_file_with_special_chars() -> Generator[Path, None, None]:
    """Create a temporary file with special characters in the name."""
    # Minimal PNG data
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
        b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    
    # Create file with special characters (spaces, symbols)
    with tempfile.NamedTemporaryFile(
        prefix='test file with spaces & symbols!',
        suffix='.png',
        delete=False
    ) as f:
        f.write(png_data)
        temp_path = Path(f.name)
    
    yield temp_path
    temp_path.unlink(missing_ok=True)


@pytest.fixture
def sample_file_formats():
    """Return a dictionary of supported file formats and their MIME types."""
    return {
        # Image formats
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        '.tif': 'image/tiff',
        '.tiff': 'image/tiff',
        '.jfif': 'image/jpeg',
        '.pjp': 'image/jpeg',
        '.apng': 'image/apng',
        '.svgz': 'image/svg+xml',
        '.heif': 'image/heif',
        '.heic': 'image/heic',
        '.xbm': 'image/x-xbitmap',
        # Audio formats
        '.mp3': 'audio/mpeg',
        '.aiff': 'audio/aiff',
        '.wma': 'audio/x-ms-wma',
        '.au': 'audio/basic',
        # Video formats
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.wmv': 'video/x-ms-wmv',
        '.flv': 'video/x-flv',
        '.webm': 'video/webm',
        '.mpeg': 'video/mpeg',
        '.mpg': 'video/mpeg',
    }


@pytest.fixture
def unsupported_file_formats():
    """Return a list of unsupported file formats."""
    return [
        '.txt', '.doc', '.docx', '.pdf', '.xlsx', '.zip',
        '.tar', '.gz', '.py', '.js', '.html', '.css',
        '.json', '.xml', '.csv', '.sql', '.exe', '.dmg'
    ]


@pytest.fixture
def create_temp_file():
    """Factory fixture for creating temporary files with custom content."""
    created_files = []
    
    def _create_file(content: bytes, suffix: str = '.tmp', prefix: str = 'test_') -> Path:
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            prefix=prefix,
            delete=False
        ) as f:
            f.write(content)
            temp_path = Path(f.name)
            created_files.append(temp_path)
            return temp_path
    
    yield _create_file
    
    # Cleanup all created files
    for file_path in created_files:
        file_path.unlink(missing_ok=True)


@pytest.fixture
def binary_file_samples():
    """Return sample binary data for different file types."""
    return {
        'png': (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
            b'\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        ),
        'jpg': (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H'
            b'\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08'
            b'\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19'
            b'\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' 
            b'",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11'
            b'\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03'
            b'\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4'
            b'\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01'
            b'\x00\x00?\x00\xaa\xff\xd9'
        ),
        'mp3': (
            b'\xff\xfb\x90\x00\x00\x03\x48\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        ),
        'mp4': (
            b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
            b'\x00\x00\x00\x08free\x00\x00\x00\x28mdat'
        ),
        'gif': (
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
            b'\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,'
            b'\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x04\x01\x00;'
        )
    }


@pytest.fixture
def file_size_variants(create_temp_file):
    """Create files of various sizes for testing."""
    def _create_sized_files(base_content: bytes, extension: str = '.png'):
        sizes = {
            'tiny': base_content,  # Original size
            'small': base_content + b'\x00' * 1024,  # +1KB
            'medium': base_content + b'\x00' * 10240,  # +10KB
            'large': base_content + b'\x00' * 102400,  # +100KB
            'xlarge': base_content + b'\x00' * 1048576,  # +1MB
        }
        
        files = {}
        for size_name, content in sizes.items():
            files[size_name] = create_temp_file(content, extension, f'test_{size_name}_')
        
        return files
    
    return _create_sized_files