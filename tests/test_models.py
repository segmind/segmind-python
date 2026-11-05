"""Tests for the Models service class."""

import warnings
from unittest import mock

import httpx
import pytest
import respx

import segmind
from segmind.client import SegmindClient
from segmind.exceptions import SegmindError
from segmind.models import _REGISTRY_URL, Models
from segmind.resource import Namespace


def _page(models, *, total=None, limit=50, offset=0, has_more=False):
    return {
        "models": models,
        "total": len(models) if total is None else total,
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
    }


@pytest.fixture
def client():
    return SegmindClient(api_key="test-key")


class TestModelsList:
    def test_is_a_namespace(self):
        client = mock.MagicMock()

        assert isinstance(Models(client), Namespace)

    @respx.mock
    def test_any_argument_reads_the_gateway_catalog_without_warning(self, client):
        route = respx.get("https://api.segmind.com/models").mock(
            return_value=httpx.Response(200, json=_page([{"slug": "flux-schnell"}]))
        )

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = client.models.list(limit=50)

        assert result["models"][0]["slug"] == "flux-schnell"
        assert result["has_more"] is False
        assert dict(route.calls.last.request.url.params) == {"limit": "50"}

    @respx.mock
    def test_an_argument_set_to_none_still_reads_the_gateway_catalog(self, client):
        """A caller passing an optional value through must get one response shape."""
        route = respx.get("https://api.segmind.com/models").mock(
            return_value=httpx.Response(200, json=_page([]))
        )

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            result = client.models.list(q=None)

        assert result["models"] == []
        assert route.calls.last.request.url.query == b""

    @respx.mock
    def test_sends_filters_as_the_gateways_query_params(self, client):
        route = respx.get("https://api.segmind.com/models").mock(
            return_value=httpx.Response(200, json=_page([]))
        )

        client.models.list(
            q="upscale",
            sort="cheapest",
            input=["image", "video"],
            output="video",
            slugs=("a", "b"),
            operations=["edit"],
            min_popularity=10,
            min_category_percentile=50,
            max_cost=0.5,
            created_after="2026-01-01",
            limit=3,
            offset=6,
        )

        params = dict(route.calls.last.request.url.params)
        assert params == {
            "q": "upscale",
            "sort": "cheapest",
            "input": "image,video",
            "output": "video",
            "slugs": "a,b",
            "operations": "edit",
            "min_popularity": "10",
            "min_category_percentile": "50",
            "max_cost": "0.5",
            "created_after": "2026-01-01",
            "limit": "3",
            "offset": "6",
        }

    @respx.mock
    def test_booleans_read_as_the_gateway_expects_and_false_is_sent(self, client):
        route = respx.get("https://api.segmind.com/models").mock(
            return_value=httpx.Response(200, json=_page([]))
        )

        client.models.list(is_new=False, include_coming_soon=True, facets=True, offset=0)

        params = dict(route.calls.last.request.url.params)
        assert params == {
            "is_new": "false",
            "include_coming_soon": "true",
            "facets": "true",
            "offset": "0",
        }

    def test_an_unknown_filter_is_refused(self, client):
        with pytest.raises(TypeError):
            client.models.list(nope=1)

    @respx.mock
    def test_follows_a_custom_base_url(self):
        route = respx.get("https://api-latest.segmind.com/models").mock(
            return_value=httpx.Response(200, json=_page([]))
        )

        SegmindClient(api_key="k", base_url="https://api-latest.segmind.com/v1").models.list(
            limit=1
        )

        assert route.called

    @respx.mock
    def test_an_error_is_a_segmind_error(self, client):
        respx.get("https://api.segmind.com/models").mock(
            return_value=httpx.Response(400, json={"error": "sort must be one of popular"})
        )

        with pytest.raises(SegmindError) as exc_info:
            client.models.list(sort="nope")

        assert exc_info.value.status == 400


class TestModelsListWithNoArguments:
    """Deprecated: this keeps its old behaviour until 2.0."""

    @respx.mock
    def test_returns_the_registry_list_and_warns(self, client):
        body = {"Inference Model Information List": [{"slug": "flux-schnell", "is_visible": True}]}
        registry = respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(200, json=body))
        catalog = respx.get("https://api.segmind.com/models")

        with pytest.warns(FutureWarning, match="from 2.0 will return a catalog page"):
            result = client.models.list()

        assert result == body
        assert registry.call_count == 1
        assert registry.calls.last.request.url.query == b""
        assert not catalog.called

    @respx.mock
    def test_an_error_is_a_segmind_error(self, client):
        respx.get(_REGISTRY_URL).mock(return_value=httpx.Response(401, json={"error": "nope"}))

        with pytest.warns(FutureWarning), pytest.raises(SegmindError) as exc_info:
            client.models.list()

        assert exc_info.value.status == 401


class TestModelsListAll:
    @respx.mock
    def test_reads_every_page(self, client):
        route = respx.get("https://api.segmind.com/models").mock(
            side_effect=[
                httpx.Response(
                    200,
                    json=_page([{"slug": "a"}, {"slug": "b"}], total=3, limit=100, has_more=True),
                ),
                httpx.Response(200, json=_page([{"slug": "c"}], total=3, limit=100, offset=2)),
            ]
        )

        result = client.models.list_all(output="video")

        assert [m["slug"] for m in result] == ["a", "b", "c"]
        first, second = (dict(call.request.url.params) for call in route.calls)
        assert first == {"output": "video", "limit": "100", "offset": "0"}
        assert second == {"output": "video", "limit": "100", "offset": "2"}

    @respx.mock
    def test_stops_on_an_empty_page_that_claims_more(self, client):
        route = respx.get("https://api.segmind.com/models").mock(
            return_value=httpx.Response(200, json=_page([], total=5, has_more=True))
        )

        assert client.models.list_all() == []
        assert route.call_count == 1

    def test_paging_is_not_a_filter(self, client):
        with pytest.raises(TypeError):
            client.models.list_all(limit=5)


class TestModelsGet:
    @respx.mock
    def test_returns_the_entry_with_its_schema(self, client):
        respx.get("https://api.segmind.com/model/flux-schnell").mock(
            return_value=httpx.Response(
                200, json={"slug": "flux-schnell", "parameters_schema": {"properties": {}}}
            )
        )

        assert "parameters_schema" in client.models.get("flux-schnell")

    @respx.mock
    def test_escapes_the_slug(self, client):
        route = respx.get("https://api.segmind.com/model/a%2Fb").mock(
            return_value=httpx.Response(200, json={"slug": "a/b"})
        )

        client.models.get("a/b")

        assert route.called

    @respx.mock
    def test_an_unknown_slug_is_a_segmind_error(self, client):
        respx.get("https://api.segmind.com/model/gone").mock(
            return_value=httpx.Response(404, json={"error": "Model 'gone' not found"})
        )

        with pytest.raises(SegmindError) as exc_info:
            client.models.get("gone")

        assert exc_info.value.status == 404


class TestModuleLevelModels:
    @pytest.mark.parametrize(
        ("call", "expected"),
        [
            (lambda: segmind.models.list(), ("list", (), {})),
            (lambda: segmind.models.list(q="x"), ("list", (), {"q": "x"})),
            (
                lambda: segmind.models.list_all(output="video"),
                ("list_all", (), {"output": "video"}),
            ),
            (lambda: segmind.models.get("a"), ("get", ("a",), {})),
        ],
    )
    def test_forwards_to_the_default_client(self, call, expected):
        name, args, kwargs = expected
        with mock.patch("segmind._get_client") as get_client:
            call()

        getattr(get_client.return_value.models, name).assert_called_once_with(*args, **kwargs)
