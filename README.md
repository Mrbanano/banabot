<div align="center">
  <img src="banabot_logo.png" alt="banabot" width="500">
  <h1>banabot: Ultra-Lightweight Personal AI Assistant</h1>
  <p>
    <a href="https://pypi.org/project/banabot-ai/"><img src="https://img.shields.io/pypi/v/banabot-ai" alt="PyPI"></a>
    <a href="https://pepy.tech/project/banabot-ai"><img src="https://static.pepy.tech/badge/banabot-ai" alt="Downloads"></a>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>
</div>

🍌 **banabot** is an **ultra-lightweight** personal AI assistant — a fork of [nanobot](https://github.com/HKUDS/nanobot)

⚡️ Delivers core agent functionality in just **~4,000** lines of code — **99% smaller** than Clawdbot's 430k+ lines.

📏 Real-time line count: **3,761 lines** (run `bash core_agent_lines.sh` to verify anytime)

## 📢 News

- **2026-02-19** 🍌 **banabot v0.2.0** released! Fork of nanobot with multi-provider web search and complete rebranding.
- **2026-02-19** 🔍 Multi-provider web search: DuckDuckGo (free, no API key), Brave, Tavily, Serper, SearXNG.
- **2026-02-19** 🎨 Complete rebranding: new logo 🍌, CLI command `banabot`, config path `~/.banabot`.

<details>
<summary>Historical news (from nanobot)</summary>

- **2026-02-17** 🎉 Released **v0.1.4** — MCP support, progress streaming, new providers. See [nanobot releases](https://github.com/HKUDS/nanobot/releases).
- **2026-02-14** 🔌 MCP support added! See [MCP section](#mcp-model-context-protocol) for details.
- **2026-02-09** 💬 Added Slack, Email, and QQ support.
- **2026-02-02** 🎉 nanobot officially launched!

</details>

## Key Features of banabot:

🪶 **Ultra-Lightweight**: Just ~4,000 lines of core agent code — 99% smaller than Clawdbot.

🔬 **Research-Ready**: Clean, readable code that's easy to understand, modify, and extend for research.

⚡️ **Lightning Fast**: Minimal footprint means faster startup, lower resource usage, and quicker iterations.

💎 **Easy-to-Use**: One-click to deploy and you're ready to go.

## 🏗️ Architecture

<p align="center">
  <img src="banabot_arch.png" alt="banabot architecture" width="800">
</p>

## ✨ Features

<table align="center">
  <tr align="center">
    <th><p align="center">📈 24/7 Real-Time Market Analysis</p></th>
    <th><p align="center">🚀 Full-Stack Software Engineer</p></th>
    <th><p align="center">📅 Smart Daily Routine Manager</p></th>
    <th><p align="center">📚 Personal Knowledge Assistant</p></th>
  </tr>
  <tr>
    <td align="center"><p align="center"><img src="case/search.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/code.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/scedule.gif" width="180" height="400"></p></td>
    <td align="center"><p align="center"><img src="case/memory.gif" width="180" height="400"></p></td>
  </tr>
  <tr>
    <td align="center">Discovery • Insights • Trends</td>
    <td align="center">Develop • Deploy • Scale</td>
    <td align="center">Schedule • Automate • Organize</td>
    <td align="center">Learn • Memory • Reasoning</td>
  </tr>
</table>

## 📦 Install

**Install from source** (latest features, recommended for development)

```bash
git clone https://github.com/Mrbanano/banabot.git
cd banabot
pip install -e .
```

**Install with [uv](https://github.com/astral-sh/uv)** (stable, fast)

```bash
uv tool install banabot-ai
```

**Install from PyPI** (stable)

```bash
pip install banabot-ai
```

## 🚀 Quick Start

> [!TIP]
> Set your API key in `~/.banabot/config.json`.
> Get API keys: [OpenRouter](https://openrouter.ai/keys) (Global) · Web search works out-of-the-box with DuckDuckGo (free)

**1. Initialize**

```bash
banabot onboard
```

**2. Configure** (`~/.banabot/config.json`)

Add or merge these **two parts** into your config (other options have defaults).

*Set your API key* (e.g. OpenRouter, recommended for global users):
```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  }
}
```

*Set your model*:
```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5"
    }
  }
}
```

**3. Chat**

```bash
banabot agent
```

That's it! You have a working AI assistant in 2 minutes.

## 💬 Chat Apps

Connect banabot to your favorite chat platform.

| Channel | What you need |
|---------|---------------|
| **Telegram** | Bot token from @BotFather |
| **Discord** | Bot token + Message Content intent |
| **WhatsApp** | QR code scan |
| **Feishu** | App ID + App Secret |
| **Mochat** | Claw token (auto-setup available) |
| **DingTalk** | App Key + App Secret |
| **Slack** | Bot token + App-Level token |
| **Email** | IMAP/SMTP credentials |
| **QQ** | App ID + App Secret |

<details>
<summary><b>Telegram</b> (Recommended)</summary>

**1. Create a bot**
- Open Telegram, search `@BotFather`
- Send `/newbot`, follow prompts
- Copy the token

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

> You can find your **User ID** in Telegram settings. It is shown as `@yourUserId`.
> Copy this value **without the `@` symbol** and paste it into the config file.


**3. Run**

```bash
banabot gateway
```

</details>

<details>
<summary><b>Mochat (Claw IM)</b></summary>

Uses **Socket.IO WebSocket** by default, with HTTP polling fallback.

**1. Ask banabot to set up Mochat for you**

Simply send this message to banabot (replace `xxx@xxx` with your real email):

```
Read https://raw.githubusercontent.com/HKUDS/MoChat/refs/heads/main/skills/nanobot/skill.md and register on MoChat. My Email account is xxx@xxx Bind me as your owner and DM me on MoChat.
```

banabot will automatically register, configure `~/.banabot/config.json`, and connect to Mochat.

**2. Restart gateway**

```bash
banabot gateway
```

That's it — banabot handles the rest!

<br>

<details>
<summary>Manual configuration (advanced)</summary>

If you prefer to configure manually, add the following to `~/.banabot/config.json`:

> Keep `claw_token` private. It should only be sent in `X-Claw-Token` header to your Mochat API endpoint.

```json
{
  "channels": {
    "mochat": {
      "enabled": true,
      "base_url": "https://mochat.io",
      "socket_url": "https://mochat.io",
      "socket_path": "/socket.io",
      "claw_token": "claw_xxx",
      "agent_user_id": "6982abcdef",
      "sessions": ["*"],
      "panels": ["*"],
      "reply_delay_mode": "non-mention",
      "reply_delay_ms": 120000
    }
  }
}
```



</details>

</details>

<details>
<summary><b>Discord</b></summary>

**1. Create a bot**
- Go to https://discord.com/developers/applications
- Create an application → Bot → Add Bot
- Copy the bot token

**2. Enable intents**
- In the Bot settings, enable **MESSAGE CONTENT INTENT**
- (Optional) Enable **SERVER MEMBERS INTENT** if you plan to use allow lists based on member data

**3. Get your User ID**
- Discord Settings → Advanced → enable **Developer Mode**
- Right-click your avatar → **Copy User ID**

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

**5. Invite the bot**
- OAuth2 → URL Generator
- Scopes: `bot`
- Bot Permissions: `Send Messages`, `Read Message History`
- Open the generated invite URL and add the bot to your server

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
<summary><b>Feishu (飞书)</b></summary>

Uses **WebSocket** long connection — no public IP required.

**1. Create a Feishu bot**
- Visit [Feishu Open Platform](https://open.feishu.cn/app)
- Create a new app → Enable **Bot** capability
- **Permissions**: Add `im:message` (send messages)
- **Events**: Add `im.message.receive_v1` (receive messages)
  - Select **Long Connection** mode (requires running banabot first to establish connection)
- Get **App ID** and **App Secret** from "Credentials & Basic Info"
- Publish the app

**2. Configure**

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "encryptKey": "",
      "verificationToken": "",
      "allowFrom": []
    }
  }
}
```

> `encryptKey` and `verificationToken` are optional for Long Connection mode.
> `allowFrom`: Leave empty to allow all users, or add `["ou_xxx"]` to restrict access.

**3. Run**

```bash
banabot gateway
```

> [!TIP]
> Feishu uses WebSocket to receive messages — no webhook or public IP needed!

</details>

<details>
<summary><b>QQ (QQ单聊)</b></summary>

Uses **botpy SDK** with WebSocket — no public IP required. Currently supports **private messages only**.

**1. Register & create bot**
- Visit [QQ Open Platform](https://q.qq.com) → Register as a developer (personal or enterprise)
- Create a new bot application
- Go to **开发设置 (Developer Settings)** → copy **AppID** and **AppSecret**

**2. Set up sandbox for testing**
- In the bot management console, find **沙箱配置 (Sandbox Config)**
- Under **在消息列表配置**, click **添加成员** and add your own QQ number
- Once added, scan the bot's QR code with mobile QQ → open the bot profile → tap "发消息" to start chatting

**3. Configure**

> - `allowFrom`: Leave empty for public access, or add user openids to restrict. You can find openids in the banabot logs when a user messages the bot.
> - For production: submit a review in the bot console and publish. See [QQ Bot Docs](https://bot.q.qq.com/wiki/) for the full publishing flow.

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

**4. Run**

```bash
banabot gateway
```

Now send a message to the bot from QQ — it should respond!

</details>

<details>
<summary><b>DingTalk (钉钉)</b></summary>

Uses **Stream Mode** — no public IP required.

**1. Create a DingTalk bot**
- Visit [DingTalk Open Platform](https://open-dev.dingtalk.com/)
- Create a new app -> Add **Robot** capability
- **Configuration**:
  - Toggle **Stream Mode** ON
- **Permissions**: Add necessary permissions for sending messages
- Get **AppKey** (Client ID) and **AppSecret** (Client Secret) from "Credentials"
- Publish the app

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

> `allowFrom`: Leave empty to allow all users, or add `["staffId"]` to restrict access.

**3. Run**

```bash
banabot gateway
```

</details>

<details>
<summary><b>Slack</b></summary>

Uses **Socket Mode** — no public URL required.

**1. Create a Slack app**
- Go to [Slack API](https://api.slack.com/apps) → **Create New App** → "From scratch"
- Pick a name and select your workspace

**2. Configure the app**
- **Socket Mode**: Toggle ON → Generate an **App-Level Token** with `connections:write` scope → copy it (`xapp-...`)
- **OAuth & Permissions**: Add bot scopes: `chat:write`, `reactions:write`, `app_mentions:read`
- **Event Subscriptions**: Toggle ON → Subscribe to bot events: `message.im`, `message.channels`, `app_mention` → Save Changes
- **App Home**: Scroll to **Show Tabs** → Enable **Messages Tab** → Check **"Allow users to send Slash commands and messages from the messages tab"**
- **Install App**: Click **Install to Workspace** → Authorize → copy the **Bot Token** (`xoxb-...`)

**3. Configure banabot**

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

**4. Run**

```bash
banabot gateway
```

DM the bot directly or @mention it in a channel — it should respond!

> [!TIP]
> - `groupPolicy`: `"mention"` (default — respond only when @mentioned), `"open"` (respond to all channel messages), or `"allowlist"` (restrict to specific channels).
> - DM policy defaults to open. Set `"dm": {"enabled": false}` to disable DMs.

</details>

<details>
<summary><b>Email</b></summary>

Give banabot its own email account. It polls **IMAP** for incoming mail and replies via **SMTP** — like a personal email assistant.

**1. Get credentials (Gmail example)**
- Create a dedicated Gmail account for your bot (e.g. `my-nanobot@gmail.com`)
- Enable 2-Step Verification → Create an [App Password](https://myaccount.google.com/apppasswords)
- Use this app password for both IMAP and SMTP

**2. Configure**

> - `consentGranted` must be `true` to allow mailbox access. This is a safety gate — set `false` to fully disable.
> - `allowFrom`: Leave empty to accept emails from anyone, or restrict to specific senders.
> - `smtpUseTls` and `smtpUseSsl` default to `true` / `false` respectively, which is correct for Gmail (port 587 + STARTTLS). No need to set them explicitly.
> - Set `"autoReplyEnabled": false` if you only want to read/analyze emails without sending automatic replies.

```json
{
  "channels": {
    "email": {
      "enabled": true,
      "consentGranted": true,
      "imapHost": "imap.gmail.com",
      "imapPort": 993,
      "imapUsername": "my-nanobot@gmail.com",
      "imapPassword": "your-app-password",
      "smtpHost": "smtp.gmail.com",
      "smtpPort": 587,
      "smtpUsername": "my-nanobot@gmail.com",
      "smtpPassword": "your-app-password",
      "fromAddress": "my-nanobot@gmail.com",
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

## 🌐 Agent Social Network

🍌 banabot is capable of linking to the agent social network (agent community). **Just send one message and your banabot joins automatically!**

| Platform | How to Join (send this message to your bot) |
|----------|-------------|
| [**Moltbook**](https://www.moltbook.com/) | `Read https://moltbook.com/skill.md and follow the instructions to join Moltbook` |
| [**ClawdChat**](https://clawdchat.ai/) | `Read https://clawdchat.ai/skill.md and follow the instructions to join ClawdChat` |

Simply send the command above to your banabot (via CLI or any chat channel), and it will handle the rest.

## ⚙️ Configuration

Config file: `~/.banabot/config.json`

### Providers

> [!TIP]
> - **Groq** provides free voice transcription via Whisper. If configured, Telegram voice messages will be automatically transcribed.
> - **Zhipu Coding Plan**: If you're on Zhipu's coding plan, set `"apiBase": "https://open.bigmodel.cn/api/coding/paas/v4"` in your zhipu provider config.
> - **MiniMax (Mainland China)**: If your API key is from MiniMax's mainland China platform (minimaxi.com), set `"apiBase": "https://api.minimaxi.com/v1"` in your minimax provider config.

| Provider | Purpose | Get API Key |
|----------|---------|-------------|
| `custom` | Any OpenAI-compatible endpoint (direct, no LiteLLM) | — |
| `openrouter` | LLM (recommended, access to all models) | [openrouter.ai](https://openrouter.ai) |
| `anthropic` | LLM (Claude direct) | [console.anthropic.com](https://console.anthropic.com) |
| `openai` | LLM (GPT direct) | [platform.openai.com](https://platform.openai.com) |
| `deepseek` | LLM (DeepSeek direct) | [platform.deepseek.com](https://platform.deepseek.com) |
| `groq` | LLM + **Voice transcription** (Whisper) | [console.groq.com](https://console.groq.com) |
| `gemini` | LLM (Gemini direct) | [aistudio.google.com](https://aistudio.google.com) |
| `minimax` | LLM (MiniMax direct) | [platform.minimax.io](https://platform.minimax.io) |
| `aihubmix` | LLM (API gateway, access to all models) | [aihubmix.com](https://aihubmix.com) |
| `siliconflow` | LLM (SiliconFlow/硅基流动, API gateway) | [siliconflow.cn](https://siliconflow.cn) |
| `dashscope` | LLM (Qwen) | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) |
| `moonshot` | LLM (Moonshot/Kimi) | [platform.moonshot.cn](https://platform.moonshot.cn) |
| `zhipu` | LLM (Zhipu GLM) | [open.bigmodel.cn](https://open.bigmodel.cn) |
| `vllm` | LLM (local, any OpenAI-compatible server) | — |
| `openai_codex` | LLM (Codex, OAuth) | `banabot provider login openai-codex` |
| `github_copilot` | LLM (GitHub Copilot, OAuth) | `banabot provider login github-copilot` |

<details>
<summary><b>OpenAI Codex (OAuth)</b></summary>

Codex uses OAuth instead of API keys. Requires a ChatGPT Plus or Pro account.

**1. Login:**
```bash
banabot provider login openai-codex
```

**2. Set model** (merge into `~/.banabot/config.json`):
```json
{
  "agents": {
    "defaults": {
      "model": "openai-codex/gpt-5.1-codex"
    }
  }
}
```

**3. Chat:**
```bash
banabot agent -m "Hello!"
```

> Docker users: use `docker run -it` for interactive OAuth login.

</details>

<details>
<summary><b>Custom Provider (Any OpenAI-compatible API)</b></summary>

Connects directly to any OpenAI-compatible endpoint — LM Studio, llama.cpp, Together AI, Fireworks, Azure OpenAI, or any self-hosted server. Bypasses LiteLLM; model name is passed as-is.

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

> For local servers that don't require a key, set `apiKey` to any non-empty string (e.g. `"no-key"`).

</details>

<details>
<summary><b>vLLM (local / OpenAI-compatible)</b></summary>

Run your own model with vLLM or any OpenAI-compatible server, then add to config:

**1. Start the server** (example):
```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct --port 8000
```

**2. Add to config** (partial — merge into `~/.banabot/config.json`):

*Provider (key can be any non-empty string for local):*
```json
{
  "providers": {
    "vllm": {
      "apiKey": "dummy",
      "apiBase": "http://localhost:8000/v1"
    }
  }
}
```

*Model:*
```json
{
  "agents": {
    "defaults": {
      "model": "meta-llama/Llama-3.1-8B-Instruct"
    }
  }
}
```

</details>

<details>
<summary><b>Adding a New Provider (Developer Guide)</b></summary>

banabot uses a **Provider Registry** (`banabot/providers/registry.py`) as the single source of truth.
Adding a new provider only takes **2 steps** — no if-elif chains to touch.

**Step 1.** Add a `ProviderSpec` entry to `PROVIDERS` in `banabot/providers/registry.py`:

```python
ProviderSpec(
    name="myprovider",                   # config field name
    keywords=("myprovider", "mymodel"),  # model-name keywords for auto-matching
    env_key="MYPROVIDER_API_KEY",        # env var for LiteLLM
    display_name="My Provider",          # shown in `banabot status`
    litellm_prefix="myprovider",         # auto-prefix: model → myprovider/model
    skip_prefixes=("myprovider/",),      # don't double-prefix
)
```

**Step 2.** Add a field to `ProvidersConfig` in `banabot/config/schema.py`:

```python
class ProvidersConfig(BaseModel):
    ...
    myprovider: ProviderConfig = ProviderConfig()
```

That's it! Environment variables, model prefixing, config matching, and `banabot status` display will all work automatically.

**Common `ProviderSpec` options:**

| Field | Description | Example |
|-------|-------------|---------|
| `litellm_prefix` | Auto-prefix model names for LiteLLM | `"dashscope"` → `dashscope/qwen-max` |
| `skip_prefixes` | Don't prefix if model already starts with these | `("dashscope/", "openrouter/")` |
| `env_extras` | Additional env vars to set | `(("ZHIPUAI_API_KEY", "{api_key}"),)` |
| `model_overrides` | Per-model parameter overrides | `(("kimi-k2.5", {"temperature": 1.0}),)` |
| `is_gateway` | Can route any model (like OpenRouter) | `True` |
| `detect_by_key_prefix` | Detect gateway by API key prefix | `"sk-or-"` |
| `detect_by_base_keyword` | Detect gateway by API base URL | `"openrouter"` |
| `strip_model_prefix` | Strip existing prefix before re-prefixing | `True` (for AiHubMix) |

</details>


### MCP (Model Context Protocol)

> [!TIP]
> The config format is compatible with Claude Desktop / Cursor. You can copy MCP server configs directly from any MCP server's README.

banabot supports [MCP](https://modelcontextprotocol.io/) — connect external tool servers and use them as native agent tools.

Add MCP servers to your `config.json`:

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

Two transport modes are supported:

| Mode | Config | Example |
|------|--------|---------|
| **Stdio** | `command` + `args` | Local process via `npx` / `uvx` |
| **HTTP** | `url` | Remote endpoint (`https://mcp.example.com/sse`) |

MCP tools are automatically discovered and registered on startup. The LLM can use them alongside built-in tools — no extra configuration needed.




### Security

> [!TIP]
> For production deployments, set `"restrictToWorkspace": true` in your config to sandbox the agent.

| Option | Default | Description |
|--------|---------|-------------|
| `tools.restrictToWorkspace` | `false` | When `true`, restricts **all** agent tools (shell, file read/write/edit, list) to the workspace directory. Prevents path traversal and out-of-scope access. |
| `channels.*.allowFrom` | `[]` (allow all) | Whitelist of user IDs. Empty = allow everyone; non-empty = only listed users can interact. |


### Web Search

banabot supports multiple search providers — **works out-of-the-box with DuckDuckGo (free, no API key required)**.

| Provider | API Key | Get Key |
|----------|---------|---------|
| `duckduckgo` (default) | No | — |
| `brave` | Yes | [Brave Search API](https://brave.com/search/api/) |
| `tavily` | Yes | [Tavily](https://tavily.com/) |
| `serper` | Yes | [Serper](https://serper.dev/) |
| `searxng` | No (self-hosted) | [SearXNG](https://searxng.org/) |

**Configuration** (`~/.banabot/config.json`):

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
          "tavily": { "apiKey": "YOUR_KEY", "enabled": false },
          "serper": { "apiKey": "YOUR_KEY", "enabled": false },
          "searxng": { "apiBase": "http://localhost:8080", "enabled": false }
        }
      }
    }
  }
}
```

If no `defaultProvider` is set, uses DuckDuckGo (free). Set `defaultProvider` to use a different provider by default.


## CLI Reference

| Command | Description |
|---------|-------------|
| `banabot onboard` | Initialize config & workspace |
| `banabot agent -m "..."` | Chat with the agent |
| `banabot agent` | Interactive chat mode |
| `banabot agent --no-markdown` | Show plain-text replies |
| `banabot agent --logs` | Show runtime logs during chat |
| `banabot gateway` | Start the gateway |
| `banabot status` | Show status |
| `banabot provider login openai-codex` | OAuth login for providers |
| `banabot channels login` | Link WhatsApp (scan QR) |
| `banabot channels status` | Show channel status |

Interactive mode exits: `exit`, `quit`, `/exit`, `/quit`, `:q`, or `Ctrl+D`.

<details>
<summary><b>Scheduled Tasks (Cron)</b></summary>

```bash
# Add a job
banabot cron add --name "daily" --message "Good morning!" --cron "0 9 * * *"
banabot cron add --name "hourly" --message "Check status" --every 3600

# List jobs
banabot cron list

# Remove a job
banabot cron remove <job_id>
```

</details>

## 🐳 Docker

> [!TIP]
> The `-v ~/.banabot:/root/.banabot` flag mounts your local config directory into the container, so your config and workspace persist across container restarts.

### Docker Compose

```bash
docker compose run --rm banabot-cli onboard   # first-time setup
vim ~/.banabot/config.json                     # add API keys
docker compose up -d banabot-gateway           # start gateway
```

```bash
docker compose run --rm banabot-cli agent -m "Hello!"   # run CLI
docker compose logs -f banabot-gateway                   # view logs
docker compose down                                      # stop
```

### Docker

```bash
# Build the image
docker build -t banabot .

# Initialize config (first time only)
docker run -v ~/.banabot:/root/.banabot --rm banabot onboard

# Edit config on host to add API keys
vim ~/.banabot/config.json

# Run gateway (connects to enabled channels, e.g. Telegram/Discord/Mochat)
docker run -v ~/.banabot:/root/.banabot -p 18790:18790 banabot gateway

# Or run a single command
docker run -v ~/.banabot:/root/.banabot --rm banabot agent -m "Hello!"
docker run -v ~/.banabot:/root/.banabot --rm banabot status
```

## 📁 Project Structure

```
banabot/
├── agent/          # 🧠 Core agent logic
│   ├── loop.py     #    Agent loop (LLM ↔ tool execution)
│   ├── context.py  #    Prompt builder
│   ├── memory.py   #    Persistent memory
│   ├── skills.py   #    Skills loader
│   ├── subagent.py #    Background task execution
│   └── tools/      #    Built-in tools (incl. spawn)
├── skills/         # 🎯 Bundled skills (github, weather, tmux...)
├── channels/       # 📱 Chat channel integrations
├── bus/            # 🚌 Message routing
├── cron/           # ⏰ Scheduled tasks
├── heartbeat/      # 💓 Proactive wake-up
├── providers/      # 🤖 LLM providers (OpenRouter, etc.)
├── session/        # 💬 Conversation sessions
├── config/         # ⚙️ Configuration
└── cli/            # 🖥️ Commands
```

## 🛠️ Development Guide

### Prerequisites

- **Python 3.11+**
- **Node.js 20+** (only needed for WhatsApp bridge)
- **Git**

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/Mrbanano/banabot.git
cd banabot

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Initialize config & workspace
banabot onboard

# 5. Add an API key to ~/.banabot/config.json (e.g. OpenRouter)
# {
#   "providers": {
#     "openrouter": { "apiKey": "sk-or-v1-xxx" }
#   }
# }

# 6. Verify everything works
banabot status
banabot agent -m "Hello!"
```

### Running Tests

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_commands.py

# Run a specific test function
pytest tests/test_commands.py::test_onboard_fresh_install

# Verbose output
pytest -v
```

Tests use `pytest-asyncio` (auto mode) for async tests and `unittest.mock` for mocking config/paths.

### Linting & Formatting

The project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting.

```bash
# Check for lint errors
ruff check banabot/

# Auto-fix lint errors
ruff check --fix banabot/

# Format code
ruff format banabot/
```

Rules configured: `E` (pycodestyle), `F` (Pyflakes), `I` (isort), `N` (naming), `W` (whitespace). Line length: 100 chars.

### Debugging

```bash
# Run agent with runtime logs visible
banabot agent -m "test" --logs

# Run gateway in verbose mode
banabot gateway --verbose
```

### Building the WhatsApp Bridge (optional)

Only needed if you're working on WhatsApp integration:

```bash
cd bridge
npm install
npm run build
```

### Key Extension Points

<details>
<summary><b>Adding a New Tool</b></summary>

1. Create `banabot/agent/tools/mytool.py` extending the `Tool` base class
2. Implement `name`, `description`, `parameters` (JSON schema), and `execute(**kwargs)`
3. Register it in the `AgentLoop` tool setup

```python
from nanobot.agent.tools.base import Tool

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
<summary><b>Adding a New Channel</b></summary>

1. Create `banabot/channels/myservice.py` extending `Channel`
2. Implement `start()`, `stop()`, and message sending logic
3. Subscribe to the inbound message bus
4. Add a config class to `banabot/config/schema.py`
5. Register in `ChannelManager.start_all()`

</details>

<details>
<summary><b>Creating a Custom Skill</b></summary>

Skills are Markdown files that give the agent domain-specific instructions:

1. Create `~/.banabot/workspace/skills/myskill/SKILL.md`
2. Write instructions, examples, and notes in Markdown
3. The agent will auto-discover and use it

See `banabot/skills/README.md` for the full skill format.

</details>

### Architecture Overview

| Component | Path | Role |
|-----------|------|------|
| **Agent Loop** | `banabot/agent/loop.py` | Core LLM ↔ tool execution cycle |
| **Context Builder** | `banabot/agent/context.py` | Assembles prompts from workspace files |
| **Memory** | `banabot/agent/memory.py` | Two-layer: `MEMORY.md` (facts) + `HISTORY.md` (events) |
| **Message Bus** | `banabot/bus/` | Async inbound/outbound queues decoupling channels from agent |
| **Provider Registry** | `banabot/providers/registry.py` | Single registry for 18+ LLM providers |
| **Session Manager** | `banabot/session/manager.py` | JSONL-based per-channel conversation storage |
| **Tool Registry** | `banabot/agent/tools/registry.py` | Manages built-in + MCP tools |
| **Channel Manager** | `banabot/channels/manager.py` | Starts/stops all enabled channel integrations |
| **Cron Service** | `banabot/cron/service.py` | Scheduled task execution (cron, interval, one-time) |
| **Config Schema** | `banabot/config/schema.py` | Pydantic models for all config sections |

### PR Workflow

```bash
# Create a feature branch
git checkout -b feature/my-feature

# Make changes, then lint and test
ruff check --fix banabot/
ruff format banabot/
pytest

# Commit and push
git add .
git commit -m "feat: description of change"
git push origin feature/my-feature
```

Then open a PR against `main`. Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.

---

## 🤝 Contribute & Roadmap

PRs welcome! The codebase is intentionally small and readable. 🤗

**Roadmap** — Pick an item and open a PR!

- [ ] **Multi-modal** — See and hear (images, voice, video)
- [ ] **Long-term memory** — Never forget important context
- [ ] **Better reasoning** — Multi-step planning and reflection
- [ ] **More integrations** — Calendar and more
- [ ] **Self-improvement** — Learn from feedback and mistakes

### Contributors

**banabot** is a fork of [nanobot](https://github.com/HKUDS/nanobot). We thank the original contributors:

<a href="https://github.com/HKUDS/nanobot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/nanobot&max=100&columns=12" alt="nanobot Contributors" />
</a>

See [CREDITS.md](./CREDITS.md) for full attribution.


## ⭐ Star History

<div align="center">
  <a href="https://star-history.com/#HKUDS/nanobot&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date" />
      <img alt="Star History Chart (original nanobot)" src="https://api.star-history.com/svg?repos=HKUDS/nanobot&type=Date" style="border-radius: 15px; box-shadow: 0 0 30px rgba(0, 217, 255, 0.3);" />
    </picture>
  </a>
</div>

<p align="center">
  <em>Thanks for visiting ✨ banabot!</em>
</p>


<p align="center">
  <sub>banabot is for educational, research, and technical exchange purposes only</sub>
</p>
