"""
Search Provider Registry — single source of truth for search provider metadata.

Adding a new search provider:
  1. Add a SearchProviderSpec to SEARCH_PROVIDERS below.
  2. Add a field to SearchProvidersConfig in config/schema.py.
  3. Implement the backend class if needed.
  Done.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class SearchProviderSpec:
    """One search provider's metadata."""
    name: str
    display_name: str
    requires_api_key: bool
    env_key: str = ""
    default_api_base: str = ""


SEARCH_PROVIDERS: tuple[SearchProviderSpec, ...] = (
    SearchProviderSpec(
        name="duckduckgo",
        display_name="DuckDuckGo",
        requires_api_key=False,
    ),
    SearchProviderSpec(
        name="brave",
        display_name="Brave Search",
        requires_api_key=True,
        env_key="BRAVE_API_KEY",
    ),
    SearchProviderSpec(
        name="tavily",
        display_name="Tavily",
        requires_api_key=True,
        env_key="TAVILY_API_KEY",
    ),
    SearchProviderSpec(
        name="serper",
        display_name="Serper (Google)",
        requires_api_key=True,
        env_key="SERPER_API_KEY",
    ),
    SearchProviderSpec(
        name="searxng",
        display_name="SearXNG",
        requires_api_key=False,
        default_api_base="",
    ),
)


def find_search_provider(name: str) -> SearchProviderSpec | None:
    """Find a search provider spec by name."""
    for spec in SEARCH_PROVIDERS:
        if spec.name == name:
            return spec
    return None


class SearchProviderBackend(ABC):
    """Abstract base class for search provider backends."""
    
    @abstractmethod
    async def search(self, query: str, count: int) -> str: ...


class DuckDuckGoBackend(SearchProviderBackend):
    """DuckDuckGo search using ddgs library (scraping-based, no API key required)."""
    
    async def search(self, query: str, count: int) -> str:
        try:
            from ddgs import DDGS
        except ImportError:
            return "Error: DuckDuckGo search requires 'ddgs' package. Install with: pip install ddgs"
        
        try:
            import asyncio
            
            def _sync_search():
                with DDGS() as ddgs:
                    return ddgs.text(query, max_results=count)
            
            results = await asyncio.to_thread(_sync_search)
            if not results:
                return f"No results for: {query}"
            
            lines = [f"Results for: {query}\n"]
            for i, item in enumerate(results[:count], 1):
                lines.append(f"{i}. {item.get('title', '')}\n   {item.get('href', '')}")
                if body := item.get("body"):
                    lines.append(f"   {body}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error searching DuckDuckGo: {e}"


class BraveSearchBackend(SearchProviderBackend):
    """Brave Search API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search(self, query: str, count: int) -> str:
        if not self.api_key:
            return "Error: Brave Search requires an API key. Get one at https://brave.com/search/api/"
        
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": count},
                    headers={"Accept": "application/json", "X-Subscription-Token": self.api_key},
                    timeout=10.0
                )
                r.raise_for_status()
            
            results = r.json().get("web", {}).get("results", [])
            if not results:
                return f"No results for: {query}"
            
            lines = [f"Results for: {query}\n"]
            for i, item in enumerate(results[:count], 1):
                lines.append(f"{i}. {item.get('title', '')}\n   {item.get('url', '')}")
                if desc := item.get("description"):
                    lines.append(f"   {desc}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error searching Brave: {e}"


class TavilyBackend(SearchProviderBackend):
    """Tavily API - designed for AI agents."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search(self, query: str, count: int) -> str:
        if not self.api_key:
            return "Error: Tavily requires an API key. Get one at https://tavily.com/"
        
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "max_results": count,
                        "include_answer": False,
                    },
                    timeout=10.0
                )
                r.raise_for_status()
            
            data = r.json()
            results = data.get("results", [])
            if not results:
                return f"No results for: {query}"
            
            lines = [f"Results for: {query}\n"]
            for i, item in enumerate(results[:count], 1):
                lines.append(f"{i}. {item.get('title', '')}\n   {item.get('url', '')}")
                if content := item.get("content"):
                    lines.append(f"   {content[:200]}...")
            return "\n".join(lines)
        except Exception as e:
            return f"Error searching Tavily: {e}"


class SerperBackend(SearchProviderBackend):
    """Serper - Google Search API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def search(self, query: str, count: int) -> str:
        if not self.api_key:
            return "Error: Serper requires an API key. Get one at https://serper.dev/"
        
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    "https://google.serper.dev/search",
                    params={"q": query, "num": count},
                    headers={"X-API-KEY": self.api_key},
                    timeout=10.0
                )
                r.raise_for_status()
            
            data = r.json()
            results = data.get("organic", [])
            if not results:
                return f"No results for: {query}"
            
            lines = [f"Results for: {query}\n"]
            for i, item in enumerate(results[:count], 1):
                lines.append(f"{i}. {item.get('title', '')}\n   {item.get('link', '')}")
                if snippet := item.get("snippet"):
                    lines.append(f"   {snippet}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error searching Serper: {e}"


class SearXNGBackend(SearchProviderBackend):
    """SearXNG - self-hosted metasearch engine."""
    
    def __init__(self, api_base: str):
        self.api_base = api_base
    
    async def search(self, query: str, count: int) -> str:
        if not self.api_base:
            return "Error: SearXNG requires 'apiBase' in config. Set it to your SearXNG instance URL."
        
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"{self.api_base.rstrip('/')}/search",
                    params={"q": query, "format": "json"},
                    timeout=10.0
                )
                r.raise_for_status()
            
            data = r.json()
            results = data.get("results", [])
            if not results:
                return f"No results for: {query}"
            
            lines = [f"Results for: {query}\n"]
            for i, item in enumerate(results[:count], 1):
                lines.append(f"{i}. {item.get('title', '')}\n   {item.get('url', '')}")
                if content := item.get("content"):
                    lines.append(f"   {content}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error searching SearXNG: {e}"


def create_search_backend(
    provider_name: str,
    api_key: str = "",
    api_base: str = "",
) -> SearchProviderBackend:
    """Create a search backend instance for the given provider."""
    backends = {
        "duckduckgo": DuckDuckGoBackend,
        "brave": BraveSearchBackend,
        "tavily": TavilyBackend,
        "serper": SerperBackend,
        "searxng": SearXNGBackend,
    }
    
    backend_class = backends.get(provider_name)
    if not backend_class:
        raise ValueError(f"Unknown search provider: {provider_name}")
    
    if provider_name == "duckduckgo":
        return backend_class()
    elif provider_name == "searxng":
        return backend_class(api_base=api_base)
    else:
        return backend_class(api_key=api_key)
