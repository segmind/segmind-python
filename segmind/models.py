from typing import Any, Dict, Iterable, List, Optional, Union
from urllib.parse import quote

from segmind.resource import Namespace, gateway_root

_MAX_PAGE_SIZE = 100


class Models(Namespace):
    """The model catalog, served by the gateway at ``GET /models``.

    Hidden, deprecated and private models are not listed.
    """

    def list(
        self,
        *,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        category: Optional[str] = None,
        modality: Optional[str] = None,
        input: Optional[Union[str, Iterable[str]]] = None,
        output: Optional[Union[str, Iterable[str]]] = None,
        provider: Optional[str] = None,
        slugs: Optional[Union[str, Iterable[str]]] = None,
        operations: Optional[Union[str, Iterable[str]]] = None,
        features: Optional[Union[str, Iterable[str]]] = None,
        min_popularity: Optional[int] = None,
        min_category_percentile: Optional[int] = None,
        min_cost: Optional[float] = None,
        max_cost: Optional[float] = None,
        max_latency: Optional[float] = None,
        is_new: Optional[bool] = None,
        created_after: Optional[str] = None,
        include_coming_soon: Optional[bool] = None,
        facets: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get one page of the catalog. Every filter is optional.

        To read further, pass ``offset`` from the previous page while
        ``has_more`` is true, or use ``list_all()``.

        Args:
            q: Free-text search; sorts by relevance unless ``sort`` is given
            sort: ``popular`` (default), ``newest``, ``name``, ``cheapest``,
                ``fastest`` or ``relevance`` (default when ``q`` is set)
            category: For example ``textToImage`` or ``imageToVideo``
            modality: Only models of this modality
            input: Models taking any of these: ``text``, ``image``, ``video``, ``audio``
            output: Models producing any of these: the input types, ``3d``,
                ``embedding`` or ``data``
            provider: Only models from this provider
            slugs: Look up these slugs, up to 100. Unlisted models resolve too
            operations: Only models supporting these operations
            features: Only models with these features
            min_popularity: Lowest popularity score, 0-100 across the catalog
            min_category_percentile: Lowest percentile, 0-100 within the category
            min_cost: Lowest observed average spend per request, in USD
            max_cost: Highest observed average spend per request, in USD
            max_latency: Highest latency, in seconds
            is_new: Only new models, or with ``False`` only established ones
            created_after: ``YYYY-MM-DD``
            include_coming_soon: Also list models that are not live yet
            facets: Also return filter counts under ``facets``
            limit: Page size, 1-100. Default 50
            offset: Models to skip

        Returns:
            ``{"models": [...], "total", "limit", "offset", "has_more"}``
        """
        params = {
            "q": q,
            "sort": sort,
            "category": category,
            "modality": modality,
            "input": _join(input),
            "output": _join(output),
            "provider": provider,
            "slugs": _join(slugs),
            "operations": _join(operations),
            "features": _join(features),
            "min_popularity": min_popularity,
            "min_category_percentile": min_category_percentile,
            "min_cost": min_cost,
            "max_cost": max_cost,
            "max_latency": max_latency,
            "is_new": is_new,
            "created_after": created_after,
            "include_coming_soon": include_coming_soon,
            "facets": facets,
            "limit": limit,
            "offset": offset,
        }
        url = f"{gateway_root(self._client.base_url)}/models"
        response = self._client._request(
            "GET", url, params={k: v for k, v in params.items() if v is not None}
        )
        return response.json()

    def list_all(self, **filters: Any) -> List[Dict[str, Any]]:
        """Get every model matching the filters, reading page after page.

        Args:
            **filters: The filters of ``list()``, except ``limit``, ``offset``
                and ``facets``

        Returns:
            The matching catalog entries
        """
        models: List[Dict[str, Any]] = []
        while True:
            page = self.list(**filters, limit=_MAX_PAGE_SIZE, offset=len(models))
            models.extend(page["models"])
            if not page.get("has_more") or not page["models"]:
                return models

    def get(self, slug: str) -> Dict[str, Any]:
        """Get one model, with its ``parameters_schema``.

        ``list()`` entries leave the schema out. A hidden, deprecated or private
        model is a 404.

        Args:
            slug: The model's slug

        Returns:
            The catalog entry plus ``parameters_schema``
        """
        url = f"{gateway_root(self._client.base_url)}/model/{quote(slug, safe='')}"
        return self._client._request("GET", url).json()


def _join(value: Optional[Union[str, Iterable[str]]]) -> Optional[str]:
    """The gateway takes a list as one comma-joined query value."""
    if value is None or isinstance(value, str):
        return value
    return ",".join(value)
