from typing import Any, Optional
from urllib.parse import quote

from segmind.resource import Namespace

REQUEST_HISTORY_URL = "https://api.spotprod.segmind.com/inference-request/request-history"


class Generations(Namespace):
    """Client for Segmind Generations API."""

    def recent(self, model_name: str) -> dict[str, Any]:
        """Get recent generations for a model.

        Args:
            model_name: Name of the model to get recent generations for (required)

        Returns:
            Dictionary containing recent generations response
        """
        params = {"model_name": model_name}
        url = "https://api.spotprod.segmind.com/inference-request/recent-generations"
        response = self._client._request("GET", url, params=params)
        return response.json()

    def list(
        self,
        page: int = 1,
        model_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get generations with pagination and filtering.

        Args:
            page: Page number for pagination (default: 1)
            model_name: Name of the model to filter by (optional)
            start_date: Start date filter in YYYY-MM-DD format (optional)
            end_date: End date filter in YYYY-MM-DD format (optional)
            user_id: UUID of the user whose generations to return (optional).
                When acting inside a team, this may be any member of that team;
                otherwise it may only be your own user id.

        Returns:
            Dictionary containing generations list response. Each row carries
            the output ``generation_url`` plus, from the request behind it,
            ``status``, ``credits_deduction`` (cost in USD), ``latency_ms``,
            ``prompt`` and the full input ``parameters``. These are ``None``
            for a generation whose request record has not landed yet. Read
            them with ``row.get(...)``: servers that predate them omit the
            keys entirely.
        """
        params = {"page": page}

        if model_name:
            params["model_name"] = model_name
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if user_id:
            params["user_id"] = user_id

        url = "https://api.spotprod.segmind.com/inference-request/generations"
        response = self._client._request("GET", url, params=params)
        return response.json()

    def history(
        self,
        page: int = 1,
        per_page: int = 20,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        model_name: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> dict[str, Any]:
        """List requests with their cost, inputs and outcome, failures included.

        Unlike :meth:`list`, which only has requests that produced an output,
        this includes failed and in-flight requests too. A request that
        produced several outputs appears once per output, each row carrying
        the request's full ``credits_deduction`` — de-duplicate on
        ``request_id`` before summing cost.

        Args:
            page: Page number for pagination (default: 1)
            per_page: Rows per page, 1-100 (default: 20)
            from_date: Start of the window, YYYY-MM-DD (default: 7 days ago)
            to_date: End of the window, YYYY-MM-DD, inclusive (default: today).
                The window may span at most 31 days.
            model_name: Filter by model slug (substring match)
            status: One of ``COMPLETED``, ``FAILED``, ``PENDING``
            user_id: UUID of the user whose requests to return. Inside a team
                this may be any member; otherwise only your own.
            user_email: Same as ``user_id``, by email. Pass one or the other.
            sort_by: ``model_created`` (default), ``model_name`` or
                ``credits_deduction``
            sort_order: ``desc`` (default) or ``asc``

        Returns:
            Paginated dictionary. Each row carries ``request_id``,
            ``model_name``, ``model_status``, ``credits_deduction`` (cost in
            USD), ``request_body`` (the inputs as sent), ``generation_url``,
            ``latency_ms``, timestamps and, for failures, ``error``.
        """
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        optional = {
            "from_date": from_date,
            "to_date": to_date,
            "model_name": model_name,
            "status": status,
            "user_id": user_id,
            "user_email": user_email,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        params.update({key: value for key, value in optional.items() if value})

        response = self._client._request("GET", REQUEST_HISTORY_URL, params=params)
        return response.json()

    def get(self, request_id: str) -> dict[str, Any]:
        """Get one of your own requests by its id, with cost, inputs and output URL.

        Not bounded by a date window, so a request of any age resolves. Only
        requests made by the calling account resolve: inside a team,
        :meth:`history` also lists teammates' requests, and passing one of
        their ids here raises a not-found error.

        Args:
            request_id: The ``request_id`` of one of your generations, as
                returned by :meth:`list` or :meth:`history`

        Returns:
            Dictionary with the same fields as a :meth:`history` row.
        """
        url = f"{REQUEST_HISTORY_URL}/{quote(request_id, safe='')}"
        response = self._client._request("GET", url)
        return response.json()
