<div align="center">
  <img src="https://raw.githubusercontent.com/Mrbanano/banabot/main/img/banabot-logo.png" alt="banabot" width="420">
  <h1>banabot 🍌</h1>
  <p>Lightweight personal AI assistant you can run anywhere — CLI, Telegram, WhatsApp, Discord, and more.</p>
</div>

---

## Install

```bash
# Recommended — fast and isolated
uv tool install banabot-ai

# Or with pip
pip install banabot-ai
```

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

---

## Chat Channels

Connect banabot to your favorite platform and run `banabot gateway` to start.

| Channel | What you need |
|---------|---------------|
| **Telegram** | Bot token from @BotFather |
| **Discord** | Bot token + Message Content intent |
| **WhatsApp** | Node.js ≥18 + QR scan |
| **Feishu** | App ID + App Secret |
| **Slack** | Bot token + App-Level token |
| **DingTalk** | App Key + App Secret |
| **Mochat** | Claw token |
| **Email** | IMAP/SMTP credentials |
| **QQ** | App ID + App Secret |

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

**5. Invite the bot** — OAuth2 → URL Generator → Scopes: `bot` → Permissions: `Send Messages`, `Read Message History`.

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

<details>
<summary><b>Slack</b></summary>

Uses **Socket Mode** — no public URL required.

**1. Create a Slack app** at [api.slack.com/apps](https://api.slack.com/apps) → From scratch.

**2. Configure the app**
- **Socket Mode**: Toggle ON → Generate App-Level Token with `connections:write` scope → copy (`xapp-...`)
- **OAuth & Permissions**: Add bot scopes: `chat:write`, `reactions:write`, `app_mentions:read`
- **Event Subscriptions**: Toggle ON → Subscribe: `message.im`, `message.channels`, `app_mention`
- **App Home**: Enable Messages Tab → Allow messages from the tab
- **Install App**: Install to Workspace → copy Bot Token (`xoxb-...`)

**3. Configure**
```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "botToken": "xoxb-...",
      "appToken": "xapp-...",
      "groupPolicy": "mention"
    }
  }
}
```
> `groupPolicy`: `"mention"` (respond only when @mentioned), `"open"` (all messages), or `"allowlist"` (specific channels).

**4. Run**
```bash
banabot gateway
```

</details>

<details>
<summary><b>Feishu (飞书)</b></summary>

Uses **WebSocket** — no public IP required.

**1. Create a Feishu app** at [open.feishu.cn](https://open.feishu.cn/app) → Enable Bot capability → Permissions: `im:message` → Events: `im.message.receive_v1` (Long Connection mode) → Publish.

**2. Configure**
```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "allowFrom": []
    }
  }
}
```
> `allowFrom`: leave empty to allow all users, or add `["ou_xxx"]` to restrict.

**3. Run**
```bash
banabot gateway
```

</details>

<details>
<summary><b>DingTalk (钉钉)</b></summary>

Uses **Stream Mode** — no public IP required.

**1. Create a bot** at [open-dev.dingtalk.com](https://open-dev.dingtalk.com/) → Add Robot capability → Toggle Stream Mode ON → Get AppKey and AppSecret.

**2. Configure**
```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "clientId": "YOUR_APP_KEY",
      "clientSecret": "YOUR_APP_SECRET",
      "allowFrom": []
    }
  }
}
```

**3. Run**
```bash
banabot gateway
```

</details>

<details>
<summary><b>Email</b></summary>

Give banabot its own email account. It polls IMAP for new mail and replies via SMTP.

**1. Get credentials** — Create a dedicated Gmail account → Enable 2-Step Verification → Create an [App Password](https://myaccount.google.com/apppasswords).

**2. Configure**
```json
{
  "channels": {
    "email": {
      "enabled": true,
      "consentGranted": true,
      "imapHost": "imap.gmail.com",
      "imapPort": 993,
      "imapUsername": "my-banabot@gmail.com",
      "imapPassword": "your-app-password",
      "smtpHost": "smtp.gmail.com",
      "smtpPort": 587,
      "smtpUsername": "my-banabot@gmail.com",
      "smtpPassword": "your-app-password",
      "fromAddress": "my-banabot@gmail.com",
      "allowFrom": ["your-real-email@gmail.com"]
    }
  }
}
```

**3. Run**
```bash
banabot gateway
```

</details>

<details>
<summary><b>Mochat (Claw IM)</b></summary>

**Ask banabot to set itself up** — send this message to your bot:

```
Read https://raw.githubusercontent.com/HKUDS/MoChat/refs/heads/main/skills/nanobot/skill.md and register on MoChat. My Email account is xxx@xxx Bind me as your owner and DM me on MoChat.
```

Then restart:
```bash
banabot gateway
```

</details>

<details>
<summary><b>QQ</b></summary>

Uses **botpy SDK** via WebSocket — private messages only.

**1. Register** at [q.qq.com](https://q.qq.com) → Create a bot → Get AppID and AppSecret.

**2. Configure**
```json
{
  "channels": {
    "qq": {
      "enabled": true,
      "appId": "YOUR_APP_ID",
      "secret": "YOUR_APP_SECRET",
      "allowFrom": []
    }
  }
}
```

**3. Run**
```bash
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
| `minimax` | MiniMax | [platform.minimax.io](https://platform.minimax.io) |
| `vllm` | Local / any OpenAI-compatible server | — |
| `custom` | Any OpenAI-compatible endpoint | — |
| `openai_codex` | Codex via OAuth | `banabot provider login openai-codex` |
| `github_copilot` | GitHub Copilot via OAuth | `banabot provider login github-copilot` |

> **Voice transcription**: configure Groq to automatically transcribe Telegram voice messages.

<details>
<summary><b>Local / custom provider</b></summary>

Connect to any OpenAI-compatible endpoint — LM Studio, llama.cpp, Together AI, Azure OpenAI, etc.

```json
{
  "providers": {
    "custom": {
      "apiKey": "your-api-key",
      "apiBase": "https://api.your-provider.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "your-model-name"
    }
  }
}
```

For local servers without auth, set `"apiKey"` to any non-empty string (e.g. `"no-key"`).

</details>

<details>
<summary><b>OAuth providers (Codex, GitHub Copilot)</b></summary>

```bash
banabot provider login openai-codex
# or
banabot provider login github-copilot
```

Then set the model:
```json
{
  "agents": {
    "defaults": { "model": "openai-codex/gpt-5.1-codex" }
  }
}
```

> Docker users: use `docker run -it` for interactive login.

</details>

<details>
<summary><b>Adding a new provider (developer guide)</b></summary>

Only two files need to change. No if-elif chains.

**1. Add a `ProviderSpec` to `PROVIDERS` in `src/banabot/providers/registry.py`:**

```python
ProviderSpec(
    name="myprovider",
    keywords=("myprovider", "mymodel"),
    env_key="MYPROVIDER_API_KEY",
    display_name="My Provider",
    litellm_prefix="myprovider",
    skip_prefixes=("myprovider/",),
)
```

**2. Add a field to `ProvidersConfig` in `src/banabot/config/schema.py`:**

```python
myprovider: ProviderConfig = Field(default_factory=ProviderConfig)
```

Done. Environment variables, model prefixing, config matching, and `banabot status` work automatically.

</details>

### Web Search

Works out-of-the-box with DuckDuckGo — no API key needed.

| Provider | Key required | Get key |
|----------|-------------|---------|
| `duckduckgo` (default) | No | — |
| `brave` | Yes | [brave.com/search/api](https://brave.com/search/api/) |
| `tavily` | Yes | [tavily.com](https://tavily.com/) |
| `serper` | Yes | [serper.dev](https://serper.dev/) |
| `searxng` | No (self-hosted) | [searxng.org](https://searxng.org/) |

```json
{
  "tools": {
    "web": {
      "search": {
        "defaultProvider": "duckduckgo",
        "providers": {
          "brave": { "apiKey": "YOUR_KEY", "enabled": true }
        }
      }
    }
  }
}
```

### MCP (Model Context Protocol)

Connect external tool servers. Compatible with Claude Desktop / Cursor config format.

```json
{
  "tools": {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
      },
      "remote": {
        "url": "https://mcp.example.com/sse"
      }
    }
  }
}
```

MCP tools are discovered and registered automatically on startup.

### Security

| Option | Default | Description |
|--------|---------|-------------|
| `tools.restrictToWorkspace` | `false` | Restricts all agent tools (shell, file ops) to the workspace directory |
| `channels.*.allowFrom` | `[]` (all) | Whitelist of user IDs. Empty = allow everyone |

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `banabot onboard` | Initialize config and workspace |
| `banabot agent` | Interactive chat (type `exit` or `Ctrl+D` to quit) |
| `banabot agent -m "..."` | Single message |
| `banabot agent --no-markdown` | Plain text output |
| `banabot agent --logs` | Show runtime logs |
| `banabot gateway` | Start gateway (all enabled channels) |
| `banabot status` | Show config and API key status |
| `banabot channels status` | Show channel status |
| `banabot channels login` | Link WhatsApp (QR scan) |
| `banabot provider login <name>` | OAuth login (openai-codex, github-copilot) |
| `banabot cron list` | List scheduled jobs |
| `banabot cron add ...` | Add a scheduled job |
| `banabot cron remove <id>` | Remove a job |

<details>
<summary><b>Cron examples</b></summary>

```bash
# Every day at 9am
banabot cron add --name "morning" --message "Good morning, check my calendar" --cron "0 9 * * *"

# Every hour
banabot cron add --name "check" --message "Any urgent emails?" --every 3600

# One time
banabot cron add --name "reminder" --message "Call dentist" --at "2026-03-01T10:00:00"

# Deliver result to Telegram
banabot cron add --name "report" --message "Summarize news" --cron "0 8 * * *" --deliver --to YOUR_USER_ID --channel telegram
```

</details>

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

# Logs
docker compose logs -f banabot-gateway
```

<details>
<summary><b>Docker without Compose</b></summary>

```bash
docker build -t banabot .
docker run -v ~/.banabot:/root/.banabot --rm banabot onboard
docker run -v ~/.banabot:/root/.banabot -p 18790:18790 banabot gateway
docker run -v ~/.banabot:/root/.banabot --rm banabot agent -m "Hello!"
```

</details>

---

## Project Structure

```
src/banabot/
├── agent/
│   ├── loop.py         # Agent loop — LLM ↔ tool execution cycle
│   ├── context.py      # Prompt builder
│   ├── memory.py       # Persistent memory (MEMORY.md + HISTORY.md)
│   ├── skills.py       # Skills loader
│   ├── subagent.py     # Background task execution
│   └── tools/          # Built-in tools (file, shell, web, message, spawn, cron)
├── skills/             # Bundled skills (github, weather, tmux, memory...)
├── channels/           # Chat channel integrations
├── bus/                # Async message routing
├── cron/               # Scheduled tasks
├── heartbeat/          # Proactive wake-up (runs every 30m)
├── providers/          # LLM provider registry
├── session/            # Per-conversation JSONL storage
├── config/             # Pydantic config schema + loader
└── cli/                # CLI commands
```

### How it works

A message comes in through a **channel** (Telegram, CLI, etc.) → lands on the **message bus** → the **agent loop** picks it up → builds a prompt with the **context builder** (system prompt + memory + history) → calls the **LLM** → executes any **tool calls** → sends the response back through the bus.

Sessions are stored as JSONL files. When a session grows beyond 50 messages, older messages are consolidated into `memory/MEMORY.md` (long-term facts) and `memory/HISTORY.md` (event log) by a background LLM call.

---

## Development

### Setup

```bash
git clone https://github.com/Mrbanano/banabot.git
cd banabot

# Install with uv (recommended)
uv sync --dev

# Or with pip
pip install -e ".[dev]"

# Initialize config and workspace
banabot onboard
banabot agent -m "Hello!"
```

### Tests

```bash
pytest
pytest tests/test_commands.py          # specific file
pytest tests/test_commands.py::test_X  # specific test
pytest -v                              # verbose
```

### Lint

```bash
ruff check src/banabot/       # check
ruff check --fix src/banabot/ # auto-fix
ruff format src/banabot/      # format
```

### Extending banabot

<details>
<summary><b>Adding a new tool</b></summary>

1. Create `src/banabot/agent/tools/mytool.py` extending `Tool`
2. Implement `name`, `description`, `parameters` (JSON schema), and `execute(**kwargs)`
3. Register it in `AgentLoop._register_default_tools()`

```python
from banabot.agent.tools.base import Tool

class MyTool(Tool):
    name = "my_tool"
    description = "Does something useful"
    parameters = {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "The input value"}
        },
        "required": ["input"]
    }

    async def execute(self, **kwargs):
        return f"Result: {kwargs['input']}"
```

</details>

<details>
<summary><b>Adding a new channel</b></summary>

1. Create `src/banabot/channels/myservice.py` extending `Channel`
2. Implement `start()`, `stop()`, and message sending
3. Subscribe to the inbound message bus
4. Add a config class to `src/banabot/config/schema.py`
5. Register in `ChannelManager.start_all()`

</details>

<details>
<summary><b>Creating a custom skill</b></summary>

Skills are Markdown files that teach the agent domain-specific behavior.

1. Create `~/.banabot/workspace/skills/myskill/SKILL.md`
2. Write instructions, examples, and context in Markdown
3. The agent auto-discovers it on next start

See `src/banabot/skills/README.md` for the full skill format and frontmatter options.

</details>

### PR Workflow

```bash
git checkout -b feat/my-feature
ruff check --fix src/banabot/ && pytest
git commit -m "feat: description"
git push origin feat/my-feature
```

Commit prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.

---

## Roadmap

See [`roadmap/index.md`](roadmap/index.md) for the full roadmap.

Highlights in progress:

- [ ] **Semantic memory** — Vector search over past conversations (episodic + summaries)
- [ ] **Onboarding** — Conversational first-run setup
- [ ] **Memory compression** — Smarter consolidation, no more lossy summaries

---

## Credits

banabot is a fork of [nanobot](https://github.com/HKUDS/nanobot). See [CREDITS.md](./CREDITS.md) for full attribution.
