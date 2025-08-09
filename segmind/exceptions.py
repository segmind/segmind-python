from typing import Optional

import httpx


def raise_for_status(response: httpx.Response) -> None:
    if response.status_code != 200:
        raise SegmindError.from_response(response)


class SegmindError(Exception):
    """Base class for all Segmind errors."""

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
        """Create a ReplicateError from an HTTP response."""

        try:
            data = response.json()
        except ValueError:
            data = {}

        return cls(
            detail=data.get("error"),
            status=response.status_code,
        )

    def to_dict(self) -> dict:
        """Get a dictionary representation of the error."""

        return {
            # "type": self.type,
            # "title": self.title,
            "status": self.status,
            "detail": self.detail,
        }

    def __str__(self) -> str:
        return "\n-----SegmindError Details-----\n" + "\n".join(
            [f"{key}: {value}" for key, value in self.to_dict().items()]
        )

    def __repr__(self) -> str:
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
