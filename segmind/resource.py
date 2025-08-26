import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from segmind.client import SegmindClient


class Namespace(abc.ABC):
    """
    A base class for representing objects of a particular type on the server.
    """

    _client: "SegmindClient"

    def __init__(self, client: "SegmindClient") -> None:
        self._client = client
