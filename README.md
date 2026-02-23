<div align="center">
  <img src="https://raw.githubusercontent.com/Mrbanano/banabot/main/img/banabot-logo.png" alt="banabot" width="420">
  <h1>banabot 🍌</h1>
  <p>
    Lightweight personal AI assistant — fork of nanobot with semantic memory and skills.
  </p>
  <p>
    <a href="https://pypi.org/project/banabot-ai/"><img src="https://img.shields.io/pypi/v/banabot-ai" alt="PyPI"></a>
    <a href="https://pepy.tech/project/banabot-ai"><img src="https://static.pepy.tech/badge/banabot-ai" alt="Downloads"></a>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

---

## What's banabot?

banabot is a **lightweight personal AI assistant** forked from [nanobot](https://github.com/HKUDS/nanobot). We keep the best of nanobot — ultra-light (~4k lines), clean code, multi-channel support — and add our own flavor:

- 🧠 **Semantic Memory v2** — Vector embeddings with fastembed + usearch. Remembers conversations semantically ("estuve en Oaxaca" → finds it later even if you don't say "Oaxaca")
- 🎯 **Skills v2** — XML-formatted prompts, auto-discovery, auto-install from ClawHub
- 🪶 **Still tiny** — Under 5k lines. Fast startup, low memory, runs anywhere
- 🔧 **Bug fixes** — Cron loop prevention, lazy loading, workspace cleanup

**Philosophy**: Same DNA as nanobot/OpenClaw, but with faster iteration and personal touches.

---

## Install

```bash
# Recommended — fast and isolated
uv tool install banabot-ai

# Or with pip
pip install banabot-ai
```

> **From source** (development):
> ```bash
> git clone https://github.com/Mrbanano/banabot.git
> cd banabot
> uv sync --dev
> ```

---

## Quick Start

**1. Initialize**
```bash
banabot onboard
```

**2. Add your API key** (`~/.banabot/config.json`)

```json
{
  "providers": {
    "openrouter": { "apiKey": "sk-or-v1-xxx" }
  },
  "agents": {
    "defaults": { "model": "anthropic/claude-opus-4-5" }
  }
}
```

> Get a key: [OpenRouter](https://openrouter.ai/keys) gives access to all major models. Web search works out-of-the-box with DuckDuckGo (free, no key needed).

**3. Chat**
```bash
banabot agent
```

**4. Enable channels** (optional)

```bash
banabot gateway
```

---

## Features

### Semantic Memory v2 🧠

Memory that actually works. Uses vector embeddings to find past conversations by meaning, not keywords.

```json
{
  "semanticMemory": {
    "enabled": true,
    "model": "BAAI/bge-small-en-v1.5",
    "maxResults": 5,
    "citation": true,
    "mmr": true
  }
}
```

- **Vector search** — fastembed + usearch for semantic recall
- **TTL support** — memories can expire
- **Citations** — knows when it's recalling past context
- **MMR** — Max Marginal Relevance for diverse results
- **Query expansion** — smarter searches

Enabled via wizard (`banabot onboard`) or manually in config.

### Skills v2 🎯

Skills teach banabot domain-specific behavior. New format with XML support:

```markdown
<!-- skill: github -->
<instructions>
You are a GitHub expert. Help with repos, issues, PRs.
</instructions>

<examples>
User: "create a repo"
→ Use tool: github_create_repo

User: "list my repos"
→ Use tool: github_list_repos
</examples>
```

Features:
- **Auto-discovery** — skills in `~/.banabot/workspace/skills/` load automatically
- **Auto-install** — agent can install skills from ClawHub registry
- **Categories** — `_core`, `_integrations`, `_tools`, `_community`
- **Validation** — truncated, emoji hints, installation guidance

### Memory System

- **Session memory** — JSONL files per conversation
- **Long-term memory** — `memory/MEMORY.md` (facts) + `memory/HISTORY.md` (events)
- **Semantic recall** — vector search over past conversations
- **Compaction** — automatic consolidation when sessions grow large
- **Session hooks** — `/new` command triggers session save

---

## Chat Channels

Connect to Telegram, Discord, WhatsApp, Slack, and more. Run `banabot gateway` to start.

| Channel | What you need |
|---------|---------------|
| **Telegram** | Bot token from @BotFather |
| **Discord** | Bot token + Message Content intent |
| **WhatsApp** | Node.js ≥18 + QR scan |
| **Feishu** | App ID + App Secret |
| **Slack** | Bot token + App-Level token |
| **Mochat** | Claw token |

<details>
<summary><b>Telegram</b> (Recommended)</summary>

**1. Create a bot** — open Telegram → search `@BotFather` → `/newbot` → copy the token.

**2. Configure**
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

> Your User ID is shown in Telegram settings as `@yourUserId`. Paste it **without the `@`**.

**3. Run**
```bash
banabot gateway
```
</details>

<details>
<summary><b>Discord</b></summary>

**1. Create a bot** at [discord.com/developers](https://discord.com/developers/applications) → New Application → Bot → Copy token.

**2. Enable intents** — Bot settings → enable **MESSAGE CONTENT INTENT**.

**3. Get your User ID** — Settings → Advanced → Developer Mode → right-click avatar → Copy User ID.

**4. Configure**
```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

**5. Invite** — OAuth2 → URL Generator → Scopes: `bot` → Permissions: `Send Messages`, `Read Message History`.

**6. Run**
```bash
banabot gateway
```
</details>

<details>
<summary><b>WhatsApp</b></summary>

Requires **Node.js ≥18**.

**1. Link device**
```bash
banabot channels login
# Scan QR with WhatsApp → Settings → Linked Devices
```

**2. Configure**
```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

**3. Run** (two terminals)
```bash
# Terminal 1
banabot channels login

# Terminal 2
banabot gateway
```
</details>

---

## Configuration

Config file: `~/.banabot/config.json`

### LLM Providers

| Provider | Purpose | Get key |
|----------|---------|---------|
| `openrouter` | All models via one key (recommended) | [openrouter.ai](https://openrouter.ai) |
| `anthropic` | Claude direct | [console.anthropic.com](https://console.anthropic.com) |
| `openai` | GPT direct | [platform.openai.com](https://platform.openai.com) |
| `deepseek` | DeepSeek direct | [platform.deepseek.com](https://platform.deepseek.com) |
| `groq` | LLM + voice transcription (Whisper) | [console.groq.com](https://console.groq.com) |
| `gemini` | Gemini direct | [aistudio.google.com](https://aistudio.google.com) |
| `aihubmix` | API gateway, all models | [aihubmix.com](https://aihubmix.com) |
| `siliconflow` | 硅基流动 gateway | [siliconflow.cn](https://siliconflow.cn) |
| `dashscope` | Qwen (阿里云) | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) |
| `moonshot` | Kimi | [platform.moonshot.cn](https://platform.moonshot.cn) |
| `zhipu` | GLM | [open.bigmodel.cn](https://open.bigmodel.cn) |
| `vllm` | Local / any OpenAI-compatible server | — |

### Semantic Memory

```json
{
  "semanticMemory": {
    "enabled": true,
    "model": "BAAI/bge-small-en-v1.5",
    "maxResults": 5,
    "citation": true,
    "mmr": true,
    "temporalDecay": 0.95,
    "queryExpansion": true
  }
}
```

### MCP (Model Context Protocol)

```json
{
  "tools": {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
      }
    }
  }
}
```

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `banabot onboard` | Initialize config and workspace |
| `banabot agent` | Interactive chat |
| `banabot agent -m "..."` | Single message |
| `banabot gateway` | Start gateway (all channels) |
| `banabot status` | Show config status |
| `banabot channels status` | Channel status |
| `banabot cron list` | List scheduled jobs |
| `banabot cron add ...` | Add scheduled job |

---

## Docker

```bash
# First-time setup
docker compose run --rm banabot-cli onboard
vim ~/.banabot/config.json  # add API keys

# Start gateway
docker compose up -d banabot-gateway

# Chat
docker compose run --rm banabot-cli agent -m "Hello!"
```

---

## Development

```bash
# Install
git clone https://github.com/Mrbanano/banabot.git
cd banabot
uv sync --dev

# Test
pytest

# Lint
ruff check --fix src/banabot/
ruff format src/banabot/

# Run
banabot onboard
banabot agent -m "Hello!"
```

---

## Project Structure

```
src/banabot/
├── agent/
│   ├── loop.py           # Agent loop — LLM ↔ tools
│   ├── context.py        # Prompt builder
│   ├── memory.py         # Persistent memory
│   ├── semantic_memory.py # Vector memory (v2)
│   ├── skills.py         # Skills loader (v2)
│   ├── hooks/            # Session hooks
│   └── tools/            # Built-in tools
├── skills/               # Bundled skills
├── channels/             # Chat integrations
├── bus/                  # Message routing
├── cron/                 # Scheduled tasks
├── providers/            # LLM providers
├── config/               # Config schema
└── cli/                  # Commands
```

---

## Roadmap

- [x] Semantic Memory v2
- [x] Skills v2
- [x] Wizard improvements
- [ ] Voice support
- [ ] Better onboarding
- [ ] More integrations

---

## Credits

**banabot** is a fork of [nanobot](https://github.com/HKUDS/nanobot) by the HKUDS team. We're grateful for their foundational work.

Special thanks to:
- The [nanobot](https://github.com/HKUDS/nanobot) team for building such a clean, extensible base
- The [OpenClaw](https://github.com/openclaw/openclaw) community for inspiration

See [CREDITS.md](./CREDITS.md) for full attribution.

---

<div align="center">
  <sub>Made with 🍌 by the banabot team</sub>
</div>
