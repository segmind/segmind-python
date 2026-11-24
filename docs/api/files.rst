Files
=====

.. automodule:: segmind.files
   :members:
   :undoc-members:
   :show-inheritance:

The files module provides functionality for uploading and managing various types of media files.

Supported File Types
--------------------

The SDK supports a wide range of file formats:

**Images**
  PNG, JPG, JPEG, GIF, BMP, WebP, AVIF, TIF, TIFF, JFIF, PJP

**Audio**
  MP3, WAV, OGG, FLAC, AAC, M4A

**Video**
  MP4, AVI, MOV, MKV, WMV, FLV, WebM

File Management
---------------

The :meth:`Files.upload` method handles file upload and returns information about the uploaded file including:

* Unique file identifier
* File URL for access
* Upload timestamp
* File metadata
