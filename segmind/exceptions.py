from typing import Optional

import httpx


def raise_for_status(response: httpx.Response) -> None:
    """Raise a SegmindError if the response status is not successful (2xx or 3xx).

    Args:
        response: HTTP response to check

    Raises:
        SegmindError: If response status code is not in the 2xx-3xx range
    """
    if not (200 <= response.status_code < 400):
        raise SegmindError.from_response(response)


class SegmindError(Exception):
    """Base class for all Segmind errors.

    Attributes:
        title: Error title (optional)
        status: HTTP status code (optional)
        detail: Error detail message (optional)
    """

    title: Optional[str] = None
    status: Optional[int] = None
    detail: Optional[str] = None

    def __init__(
        self,
        status: Optional[int] = None,
        detail: Optional[str] = None,
    ) -> None:
        self.status = status
        self.detail = detail

    @classmethod
    def from_response(cls, response: httpx.Response) -> "SegmindError":
        """Create a SegmindError from an HTTP response.

        Args:
            response: HTTP response object

        Returns:
            SegmindError instance created from the response
        """
        try:
            data = response.json()
            # Handle non-dict JSON (e.g., lists)
            if not isinstance(data, dict):
                data = {}
        except ValueError:
            data = {}

        return cls(
            detail=data.get("error"),
            status=response.status_code,
        )

    def to_dict(self) -> dict:
        """Get a dictionary representation of the error.

        Returns:
            Dictionary containing error details
        """
        return {
            # "type": self.type,
            # "title": self.title,
            "status": self.status,
            "detail": self.detail,
        }

    def __str__(self) -> str:
        """Return a string representation of the error.

        Returns:
            Formatted error string
        """
        return "\n-----SegmindError Details-----\n" + "\n".join(
            [f"{key}: {value}" for key, value in self.to_dict().items()]
        )

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the error.

        Returns:
            String representation for debugging
        """
        class_name = self.__class__.__name__
        params = ", ".join(
            [
                # f"type={self.type}",
                # f"title={self.title}",
                f"status={self.status}",
                f"detail={self.detail}",
            ]
        )
        return f"{class_name}({params})"
