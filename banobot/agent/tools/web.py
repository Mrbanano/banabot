"""Web tools: web_search and web_fetch."""

import html
import json
import os
import re
from typing import Any, TYPE_CHECKING
from urllib.parse import urlparse

import httpx

from banobot.agent.tools.base import Tool

if TYPE_CHECKING:
    from banobot.config.schema import WebSearchConfig

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) AppleWebKit/537.36"
MAX_REDIRECTS = 5


def _strip_tags(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r'<script[\s\S]*?</script>', '', text, flags=re.I)
    text = re.sub(r'<style[\s\S]*?</style>', '', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()


def _normalize(text: str) -> str:
    """Normalize whitespace."""
    text = re.sub(r'[ \t]+', ' ', text)
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def _validate_url(url: str) -> tuple[bool, str]:
    """Validate URL: must be http(s) with valid domain."""
    try:
        p = urlparse(url)
        if p.scheme not in ('http', 'https'):
            return False, f"Only http/https allowed, got '{p.scheme or 'none'}'"
        if not p.netloc:
            return False, "Missing domain"
        return True, ""
    except Exception as e:
        return False, str(e)


class WebSearchTool(Tool):
    """Search the web using configurable search providers."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web. Returns titles, URLs, and snippets."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "count": {"type": "integer", "description": "Results (1-10)", "minimum": 1, "maximum": 10}
            },
            "required": ["query"]
        }

    def __init__(self, config: "WebSearchConfig | None" = None):
        from banobot.config.schema import WebSearchConfig
        self.config = config or WebSearchConfig()

    def _get_backend(self, provider_name: str):
        from banobot.agent.tools.search_registry import create_search_backend
        provider_cfg = getattr(self.config.providers, provider_name, None)
        if not provider_cfg:
            return None
        return create_search_backend(
            provider_name,
            api_key=provider_cfg.api_key,
            api_base=provider_cfg.api_base,
        )

    def _get_providers_to_try(self) -> list[str]:
        """Get ordered list of providers to try: default first, then others."""
        from banobot.agent.tools.search_registry import SEARCH_PROVIDERS
        providers = [self.config.default_provider]
        for spec in SEARCH_PROVIDERS:
            if spec.name not in providers:
                providers.append(spec.name)
        return providers

    async def execute(self, query: str, count: int | None = None, **kwargs: Any) -> str:
        from banobot.agent.tools.search_registry import find_search_provider
        n = min(max(count or self.config.max_results, 1), 10)
        errors = []
        
        for provider_name in self._get_providers_to_try():
            provider_cfg = getattr(self.config.providers, provider_name, None)
            if not provider_cfg or not provider_cfg.enabled:
                continue
            
            spec = find_search_provider(provider_name)
            if not spec:
                continue
            
            if spec.requires_api_key and not provider_cfg.api_key:
                continue
            if provider_name == "searxng" and not provider_cfg.api_base:
                continue
            
            try:
                backend = self._get_backend(provider_name)
                result = await backend.search(query, n)
                if result.lower().startswith("error"):
                    errors.append(f"{provider_name}: {result}")
                    continue
                return result
            except Exception as e:
                errors.append(f"{provider_name}: {str(e)}")
                continue
        
        if errors:
            return f"Search failed for all providers:\n" + "\n".join(errors)
        return f"No search provider available for query: {query}"


class WebFetchTool(Tool):
    """Fetch and extract content from a URL using Readability."""

    @property
    def name(self) -> str:
        return "web_fetch"

    @property
    def description(self) -> str:
        return "Fetch URL and extract readable content (HTML → markdown/text)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "extractMode": {"type": "string", "enum": ["markdown", "text"], "default": "markdown"},
                "maxChars": {"type": "integer", "minimum": 100}
            },
            "required": ["url"]
        }

    def __init__(self, max_chars: int = 50000):
        self.max_chars = max_chars

    async def execute(self, url: str, extractMode: str = "markdown", maxChars: int | None = None, **kwargs: Any) -> str:
        from readability import Document

        max_chars = maxChars or self.max_chars

        is_valid, error_msg = _validate_url(url)
        if not is_valid:
            return json.dumps({"error": f"URL validation failed: {error_msg}", "url": url})

        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                max_redirects=MAX_REDIRECTS,
                timeout=30.0
            ) as client:
                r = await client.get(url, headers={"User-Agent": USER_AGENT})
                r.raise_for_status()

            ctype = r.headers.get("content-type", "")

            if "application/json" in ctype:
                text, extractor = json.dumps(r.json(), indent=2), "json"
            elif "text/html" in ctype or r.text[:256].lower().startswith(("<!doctype", "<html")):
                doc = Document(r.text)
                content = self._to_markdown(doc.summary()) if extractMode == "markdown" else _strip_tags(doc.summary())
                text = f"# {doc.title()}\n\n{content}" if doc.title() else content
                extractor = "readability"
            else:
                text, extractor = r.text, "raw"

            truncated = len(text) > max_chars
            if truncated:
                text = text[:max_chars]

            return json.dumps({"url": url, "finalUrl": str(r.url), "status": r.status_code,
                              "extractor": extractor, "truncated": truncated, "length": len(text), "text": text})
        except Exception as e:
            return json.dumps({"error": str(e), "url": url})

    def _to_markdown(self, html: str) -> str:
        text = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
                      lambda m: f'[{_strip_tags(m[2])}]({m[1]})', html, flags=re.I)
        text = re.sub(r'<h([1-6])[^>]*>([\s\S]*?)</h\1>',
                      lambda m: f'\n{"#" * int(m[1])} {_strip_tags(m[2])}\n', text, flags=re.I)
        text = re.sub(r'<li[^>]*>([\s\S]*?)</li>', lambda m: f'\n- {_strip_tags(m[1])}', text, flags=re.I)
        text = re.sub(r'</(p|div|section|article)>', '\n\n', text, flags=re.I)
        text = re.sub(r'<(br|hr)\s*/?>', '\n', text, flags=re.I)
        return _normalize(_strip_tags(text))
