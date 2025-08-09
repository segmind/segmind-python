from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SegmindResponse(BaseModel):
    """Raw response from Segmind API"""

    content: bytes
    headers: Dict[str, str]
    status_code: int


class ImageGenerationResponse(BaseModel):
    """Response model for image generation endpoints"""

    image_data: Optional[bytes] = None
    base64_string: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TextGenerationResponse(BaseModel):
    """Response model for text generation endpoints"""

    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VideoGenerationResponse(BaseModel):
    """Response model for video generation endpoints"""

    video_data: Optional[bytes] = None
    video_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
