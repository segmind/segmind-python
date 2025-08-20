import contextlib
import json
import time
from typing import Any, Dict, Optional

from segmind.resource import Namespace


class PixelFlows(Namespace):
    """Client for Segmind PixelFlows API with polling support."""

    def run(
        self,
        workflow_id: Optional[str] = None,
        workflow_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        poll: bool = True,
        poll_interval: int = 2,
        max_wait_time: int = 300,
    ) -> Dict[str, Any]:
        """Run a workflow and optionally poll for results.

        Args:
            workflow_id: The workflow ID to execute (mutually exclusive with workflow_url)
            workflow_url: Full URL to the workflow (mutually exclusive with workflow_id)
            data: Input data for the workflow
            poll: Whether to poll for results (default: True)
            poll_interval: Seconds between polling requests (default: 2)
            max_wait_time: Maximum seconds to wait for results (default: 300)

        Returns:
            Dictionary containing the workflow response
        """
        # Validate inputs
        if not workflow_id and not workflow_url:
            raise ValueError("Either workflow_id or workflow_url must be provided")

        # Construct URL
        url = f"https://api.segmind.com/workflows/{workflow_id}" if workflow_id else workflow_url

        # Submit workflow request using the client
        response = self._client._request("POST", url, json=data or {})

        result = response.json()

        # If not polling, return initial response
        if not poll:
            return result

        # Extract poll_id (from request_id field) and poll_url
        poll_id = result.get("request_id")  # API returns this as request_id
        poll_url = result.get("poll_url")

        if not poll_url and not poll_id:
            return result

        # Construct poll URL if only poll_id is provided
        # TODO: this is not correct, we need to use the poll_url from the response
        if not poll_url and poll_id:
            poll_url = f"https://api.segmind.com/workflows/request/{poll_id}"

        # Poll for results
        return self._poll_for_results(poll_url, poll_interval, max_wait_time)

    def _poll_for_results(
        self, poll_url: str, poll_interval: int, max_wait_time: int
    ) -> Dict[str, Any]:
        """Poll the API until the workflow completes or times out.

        Args:
            poll_url: URL to poll for status
            poll_interval: Seconds between polling requests
            max_wait_time: Maximum seconds to wait

        Returns:
            Final workflow response
        """
        start_time = time.time()

        while True:
            # Check if we've exceeded max wait time
            if time.time() - start_time > max_wait_time:
                return {
                    "status": "TIMEOUT",
                    "error_message": f"Request timed out after {max_wait_time} seconds",
                }

            # Poll for status using the client
            response = self.client._request("GET", poll_url)

            result = response.json()
            status = result.get("status", "")

            # Check if request is complete
            if status == "COMPLETED":
                # Parse output if it's a string
                if "output" in result and isinstance(result["output"], str):
                    with contextlib.suppress(json.JSONDecodeError, TypeError):
                        result["output"] = json.loads(result["output"])
                return result

            elif status == "FAILED":
                return result

            elif status in ["QUEUED", "PROCESSING"]:
                # Continue polling
                time.sleep(poll_interval)

            else:
                # Unknown status, return as-is
                return result

    def get_status(
        self, poll_id: Optional[str] = None, poll_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the status of a workflow request.

        Args:
            poll_id: The poll ID to check (mutually exclusive with poll_url)
            poll_url: Full URL to poll for status (mutually exclusive with poll_id)

        Returns:
            Current status and output of the request
        """
        # Validate inputs
        if not poll_id and not poll_url:
            raise ValueError("Either poll_id or poll_url must be provided")
        if poll_id and poll_url:
            raise ValueError("Only one of poll_id or poll_url should be provided")

        # Construct URL
        url = f"{self.workflows_base}/request/{poll_id}" if poll_id else poll_url

        response = self.client._request("GET", url)

        result = response.json()

        # Parse output if it's a string and status is COMPLETED
        if result.get("status") == "COMPLETED" and isinstance(result.get("output", None), str):
            with contextlib.suppress(json.JSONDecodeError, TypeError):
                result["output"] = json.loads(result["output"])

        return result

    def poll(
        self,
        poll_id: Optional[str] = None,
        poll_url: Optional[str] = None,
        poll_interval: int = 2,
        max_wait_time: int = 300,
    ) -> Dict[str, Any]:
        """Poll for workflow results until completion or timeout.

        Args:
            poll_id: The poll ID to poll (mutually exclusive with poll_url)
            poll_url: Full URL to poll for status (mutually exclusive with poll_id)
            poll_interval: Seconds between polling requests (default: 2)
            max_wait_time: Maximum seconds to wait for results (default: 300)

        Returns:
            Final workflow response
        """
        # Validate inputs
        if not poll_id and not poll_url:
            raise ValueError("Either poll_id or poll_url must be provided")

        # Construct URL
        url = f"{self.workflows_base}/request/{poll_id}" if poll_id else poll_url

        return self._poll_for_results(url, poll_interval, max_wait_time)
