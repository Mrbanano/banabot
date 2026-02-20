"""Tests for web search and fetch tools."""

import pytest

from banabot.agent.tools.search_registry import (
    SEARCH_PROVIDERS,
    BraveSearchBackend,
    DuckDuckGoBackend,
    SearchProviderSpec,
    SearXNGBackend,
    SerperBackend,
    TavilyBackend,
    create_search_backend,
    find_search_provider,
)
from banabot.agent.tools.web import (
    WebFetchTool,
    WebSearchTool,
    _normalize,
    _strip_tags,
    _validate_url,
)


class TestSearchProviders:
    """Tests for search provider registry."""

    def test_search_providers_contains_all_expected(self):
        """Verify all expected search providers are defined."""
        provider_names = {spec.name for spec in SEARCH_PROVIDERS}
        expected = {"duckduckgo", "brave", "tavily", "serper", "searxng"}
        assert expected.issubset(provider_names)

    def test_duckduckgo_no_api_key_required(self):
        """DuckDuckGo should not require an API key."""
        spec = find_search_provider("duckduckgo")
        assert spec is not None
        assert spec.requires_api_key is False

    def test_brave_requires_api_key(self):
        """Brave should require an API key."""
        spec = find_search_provider("brave")
        assert spec is not None
        assert spec.requires_api_key is True
        assert spec.env_key == "BRAVE_API_KEY"

    def test_tavily_requires_api_key(self):
        """Tavily should require an API key."""
        spec = find_search_provider("tavily")
        assert spec is not None
        assert spec.requires_api_key is True
        assert spec.env_key == "TAVILY_API_KEY"

    def test_serper_requires_api_key(self):
        """Serper should require an API key."""
        spec = find_search_provider("serper")
        assert spec is not None
        assert spec.requires_api_key is True
        assert spec.env_key == "SERPER_API_KEY"

    def test_searxng_no_api_key_required(self):
        """SearXNG should not require an API key."""
        spec = find_search_provider("searxng")
        assert spec is not None
        assert spec.requires_api_key is False

    def test_find_search_provider_returns_spec(self):
        """find_search_provider should return correct spec."""
        spec = find_search_provider("duckduckgo")
        assert isinstance(spec, SearchProviderSpec)
        assert spec.name == "duckduckgo"

    def test_find_search_provider_returns_none_for_unknown(self):
        """find_search_provider should return None for unknown provider."""
        spec = find_search_provider("unknown_provider")
        assert spec is None


class TestCreateSearchBackend:
    """Tests for search backend creation."""

    def test_create_duckduckgo_backend(self):
        """Should create DuckDuckGoBackend without API key."""
        backend = create_search_backend("duckduckgo")
        assert isinstance(backend, DuckDuckGoBackend)

    def test_create_brave_backend_with_api_key(self):
        """Should create BraveSearchBackend with API key."""
        backend = create_search_backend("brave", api_key="test_key")
        assert isinstance(backend, BraveSearchBackend)
        assert backend.api_key == "test_key"

    def test_create_tavily_backend_with_api_key(self):
        """Should create TavilyBackend with API key."""
        backend = create_search_backend("tavily", api_key="test_key")
        assert isinstance(backend, TavilyBackend)
        assert backend.api_key == "test_key"

    def test_create_serper_backend_with_api_key(self):
        """Should create SerperBackend with API key."""
        backend = create_search_backend("serper", api_key="test_key")
        assert isinstance(backend, SerperBackend)
        assert backend.api_key == "test_key"

    def test_create_searxng_backend_with_api_base(self):
        """Should create SearXNGBackend with API base."""
        backend = create_search_backend("searxng", api_base="http://localhost:8080")
        assert isinstance(backend, SearXNGBackend)
        assert backend.api_base == "http://localhost:8080"

    def test_create_unknown_provider_raises_error(self):
        """Should raise ValueError for unknown provider."""
        with pytest.raises(ValueError, match="Unknown search provider"):
            create_search_backend("unknown_provider")


class TestWebHelpers:
    """Tests for web tool helper functions."""

    def test_strip_tags_removes_html(self):
        """_strip_tags should remove HTML tags."""
        html = "<p>Hello <b>World</b></p>"
        result = _strip_tags(html)
        assert "<" not in result
        assert "Hello World" in result

    def test_strip_tags_decodes_entities(self):
        """_strip_tags should decode HTML entities."""
        html = "&lt;script&gt;"
        result = _strip_tags(html)
        assert result == "<script>"

    def test_strip_tags_removes_scripts(self):
        """_strip_tags should remove script tags."""
        html = "<script>alert('xss')</script><p>Hello</p>"
        result = _strip_tags(html)
        assert "script" not in result.lower()
        assert "Hello" in result

    def test_strip_tags_removes_styles(self):
        """_strip_tags should remove style tags."""
        html = "<style>.foo { color: red; }</style><p>Hello</p>"
        result = _strip_tags(html)
        assert "style" not in result.lower()
        assert "Hello" in result

    def test_normalize_whitespace(self):
        """_normalize should normalize whitespace."""
        text = "Hello    World\n\n\n\nTest"
        result = _normalize(text)
        assert "    " not in result
        assert "\n\n\n\n" not in result

    def test_validate_url_valid_https(self):
        """_validate_url should accept valid HTTPS URLs."""
        valid, error = _validate_url("https://example.com")
        assert valid is True
        assert error == ""

    def test_validate_url_valid_http(self):
        """_validate_url should accept valid HTTP URLs."""
        valid, error = _validate_url("http://example.com")
        assert valid is True
        assert error == ""

    def test_validate_url_rejects_non_http(self):
        """_validate_url should reject non-HTTP schemes."""
        valid, error = _validate_url("ftp://example.com")
        assert valid is False
        assert "http/https allowed" in error

    def test_validate_url_rejects_missing_domain(self):
        """_validate_url should reject URLs without domain."""
        valid, error = _validate_url("http://")
        assert valid is False
        assert "domain" in error.lower()

    def test_validate_url_rejects_empty(self):
        """_validate_url should reject empty string."""
        valid, error = _validate_url("")
        assert valid is False


class TestWebSearchTool:
    """Tests for WebSearchTool."""

    def test_web_search_tool_name(self):
        """WebSearchTool should have correct name."""
        tool = WebSearchTool()
        assert tool.name == "web_search"

    def test_web_search_tool_description(self):
        """WebSearchTool should have description."""
        tool = WebSearchTool()
        assert "Search" in tool.description
        assert "web" in tool.description.lower()

    def test_web_search_tool_parameters(self):
        """WebSearchTool should have correct parameters."""
        tool = WebSearchTool()
        params = tool.parameters
        assert "query" in params["required"]
        assert "count" in params["properties"]

    def test_web_search_get_providers_to_try(self):
        """WebSearchTool should return ordered list of providers."""
        from banabot.config.schema import WebSearchConfig

        config = WebSearchConfig()
        tool = WebSearchTool(config)
        providers = tool._get_providers_to_try()

        assert config.default_provider in providers
        assert "duckduckgo" in providers


class TestWebFetchTool:
    """Tests for WebFetchTool."""

    def test_web_fetch_tool_name(self):
        """WebFetchTool should have correct name."""
        tool = WebFetchTool()
        assert tool.name == "web_fetch"

    def test_web_fetch_tool_description(self):
        """WebFetchTool should have description."""
        tool = WebFetchTool()
        assert "Fetch" in tool.description
        assert "URL" in tool.description

    def test_web_fetch_tool_parameters(self):
        """WebFetchTool should have correct parameters."""
        tool = WebFetchTool()
        params = tool.parameters
        assert "url" in params["required"]
        assert "extractMode" in params["properties"]
        assert "maxChars" in params["properties"]

    def test_web_fetch_default_max_chars(self):
        """WebFetchTool should have default max_chars."""
        tool = WebFetchTool()
        assert tool.max_chars == 50000

    def test_web_fetch_custom_max_chars(self):
        """WebFetchTool should accept custom max_chars."""
        tool = WebFetchTool(max_chars=10000)
        assert tool.max_chars == 10000

    def test_web_fetch_extract_mode_defaults_to_markdown(self):
        """WebFetchTool should default extractMode to markdown."""
        tool = WebFetchTool()
        params = tool.parameters
        assert params["properties"]["extractMode"]["default"] == "markdown"
