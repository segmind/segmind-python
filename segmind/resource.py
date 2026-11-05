import abc
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from segmind.client import SegmindClient


def gateway_root(base_url: str) -> str:
    """The gateway's root URL: `base_url` without its trailing `/vN` segment.

    Deriving it keeps callers who override base_url for staging
    (`api-latest.segmind.com/v1`) on the host they chose.
    """
    return re.sub(r"/v\d+$", "", base_url.rstrip("/"))


class Namespace(abc.ABC):
    """
    A base class for representing objects of a particular type on the server.
    """

    _client: "SegmindClient"

    def __init__(self, client: "SegmindClient") -> None:
        self._client = client
