from typing import Any, Optional

from segmind.resource import Namespace


class Finetune(Namespace):
    """Client for Segmind Finetune API."""

    base_url = "https://api.segmind.com/finetune/request"

    def submit(
        self,
        name: str,
        data_source_path: str,
        instance_prompt: str,
        trigger_word: str,
        base_model: str,
        train_type: str,
        machine_type: str,
        theme: Optional[str] = None,
        segmind_public: bool = False,
        advance_parameters: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Initiate a new fine-tuning request."""

        payload: dict[str, Any] = {
            "name": name,
            "data_source_path": data_source_path,
            "instance_prompt": instance_prompt,
            "trigger_word": trigger_word,
            "base_model": base_model,
            "train_type": train_type,
            "machine_type": machine_type,
            "segmind_public": segmind_public,
        }
        if theme is not None:
            payload["theme"] = theme
        if advance_parameters is not None:
            payload["advance_parameters"] = advance_parameters

        url = f"{self.base_url}/submit"
        response = self._client._request("POST", url, json=payload)
        return response.json()

    def details(self, request_id: str) -> dict[str, Any]:
        """Get details for a specific fine-tune request."""
        url = f"{self.base_url}/details"
        payload = {"request_id": request_id}
        response = self._client._request("GET", url, json=payload)
        return response.json()

    def list(self) -> list[dict[str, Any]]:
        """List fine-tune requests."""
        url = f"{self.base_url}/list"
        response = self._client._request("GET", url)
        return response.json()

    def upload_presigned_url(self, name: str) -> dict[str, str]:
        """Get pre-signed URL to upload fine-tune dataset zip."""
        url = f"{self.base_url}/upload/pre-signed-url"
        payload = {"name": name}
        response = self._client._request("GET", url, json=payload)
        return response.json()

    def access_update(self, request_id: str, segmind_public: bool) -> dict[str, Any]:
        """Update access settings for a fine-tuned model."""
        url = f"{self.base_url}/access-update"
        form = {"request_id": request_id, "segmind_public": str(segmind_public)}
        response = self._client._request("PUT", url, data=form)
        return response.json() if response.content else {"status": response.status_code}

    def file_download(self, cloud_storage_url: str) -> str:
        """Generate presigned download URL for the fine-tuned model file."""
        url = f"{self.base_url}/file/download"
        form = {"cloud_storage_url": cloud_storage_url}
        response = self._client._request("GET", url, data=form)
        # Endpoint returns plain text URL
        try:
            return response.text
        except Exception:  # Fallback in case of binary
            return response.content.decode("utf-8")
