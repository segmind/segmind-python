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
  PNG, JPG, JPEG, GIF, BMP, WebP, SVG, ICO, TIF, TIFF, JFIF, PJP, APNG, SVGZ, HEIF, HEIC, XBM

**Audio**
  MP3, AIFF, WMA, AU

**Video**
  MP4, AVI, MOV, MKV, WMV, FLV, WebM, MPEG, MPG

File Management
---------------

The :meth:`Files.upload` method handles file upload and returns information about the uploaded file including:

* Unique file identifier
* File URL for access
* Upload timestamp
* File metadata
