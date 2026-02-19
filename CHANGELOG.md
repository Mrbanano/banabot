# Changelog

All notable changes to banobot will be documented in this file.

## [0.1.0] - 2026-02-19

### Added

#### Multi-Provider Web Search System

Completely redesigned the web search architecture to support multiple search providers with automatic fallback.

**New Features:**
- **Multiple search providers**: DuckDuckGo, Brave, Tavily, Serper, and SearXNG
- **Out-of-the-box search**: DuckDuckGo works without any API key (free)
- **Automatic runtime fallback**: If a provider fails, automatically tries the next available provider
- **Flexible configuration**: Configure multiple providers and set a default

**New Files:**
- `nanobot/agent/tools/search_registry.py` - Search provider registry and backends (190 lines)

**Modified Files:**
- `pyproject.toml` - Added `ddgs>=9.0.0` dependency
- `nanobot/config/schema.py` - New `SearchProvidersConfig` and enhanced `WebSearchConfig`
- `nanobot/agent/tools/web.py` - `WebSearchTool` now uses the provider registry
- `nanobot/agent/loop.py` - Changed `brave_api_key` → `web_search_config`
- `nanobot/agent/subagent.py` - Changed `brave_api_key` → `web_search_config`
- `nanobot/cli/commands.py` - Updated to pass `web_search_config`
- `README.md` - New "Web Search" section with provider documentation
- `workspace/TOOLS.md` - Updated tool documentation

**Configuration Example:**
```json
{
  "tools": {
    "web": {
      "search": {
        "defaultProvider": "duckduckgo",
        "maxResults": 5,
        "providers": {
          "brave": { "apiKey": "YOUR_KEY", "enabled": true },
          "duckduckgo": { "enabled": true },
          "tavily": { "apiKey": "YOUR_KEY", "enabled": true }
        }
      }
    }
  }
}
```

**Supported Providers:**

| Provider | API Key | Notes |
|----------|---------|-------|
| `duckduckgo` | No | Free, works out-of-the-box (default) |
| `brave` | Yes | Brave Search API |
| `tavily` | Yes | Optimized for AI agents |
| `serper` | Yes | Google Search API |
| `searxng` | No (self-hosted) | Requires `apiBase` config |

**Impact:**
- Code size: ~200 lines added (still lightweight at ~4,000 total)
- Zero configuration needed for basic web search functionality
- Follows the same pattern as LLM provider registry for consistency
