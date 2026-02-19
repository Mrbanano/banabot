# Changelog

All notable changes to banobot will be documented in this file.

## [0.2.0] - 2026-02-19

### Added

#### Interactive CLI Improvements

Enhanced CLI with better branding and user experience.

**Changes:**
- Changed logo from 🐈 to 🍌
- Updated all CLI commands and descriptions to banobot branding
- Updated all user-facing messages and prompts
- Improved command help text

**Modified Files:**
- `banobot/__init__.py` - New logo 🍌
- `banobot/cli/commands.py` - All CLI text updated
- `banobot/agent/context.py` - Agent identity updated
- All channel files - Discord, Telegram, Email branding

---

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
- `banobot/agent/tools/search_registry.py` - Search provider registry and backends (190 lines)

**Modified Files:**
- `pyproject.toml` - Added `ddgs>=9.0.0` dependency
- `banobot/config/schema.py` - New `SearchProvidersConfig` and enhanced `WebSearchConfig`
- `banobot/agent/tools/web.py` - `WebSearchTool` now uses the provider registry
- `banobot/agent/loop.py` - Changed `brave_api_key` → `web_search_config`
- `banobot/agent/subagent.py` - Changed `brave_api_key` → `web_search_config`
- `banobot/cli/commands.py` - Updated to pass `web_search_config`
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

---

## [0.0.1] - 2026-02-19

### Added

#### Birth of banobot 🍌

**banobot** is born as a fork of [nanobot](https://github.com/HKUDS/nanobot).

**Rebranding Changes:**
- Package renamed: `nanobot-ai` → `banobot-ai`
- CLI command renamed: `nanobot` → `banobot`
- Config path changed: `~/.nanobot` → `~/.banobot`
- Environment variables: `NANOBOT_*` → `BANOBOT_*`
- Directory renamed: `nanobot/` → `banobot/`

**New Files:**
- `CREDITS.md` - Attribution to original nanobot contributors
- `REBRAND_PLAN.md` - Complete migration documentation
- `CHANGELOG.md` - This file

**Modified Files:**
- `LICENSE` - Added banobot copyright while preserving original
- `pyproject.toml` - Package name and configuration
- `README.md` - Updated branding with fork attribution
- `SECURITY.md` - Updated references
- All Python files - Imports updated
- All documentation files - References updated

**Key Decisions:**
- MIT License allows full rebranding (only requires attribution)
- Original contributors credited in CREDITS.md
- Git history preserved (not rewritten) - simpler and safer approach

---

> **Note on Git History**: The git history was NOT rewritten to reflect version numbers. This is intentional - rewriting git history is destructive, complex, and can cause issues with forks and clones. Instead, we use semantic versioning in the code (pyproject.toml, __init__.py) and document releases properly in CHANGELOG.md. This is a common and accepted practice in open source.
