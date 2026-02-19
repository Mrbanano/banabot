"""🍌 Banabot Config Wizard — interactive configuration for everyone.

Guided flow: language → provider → model → API key → channel → done.
Uses InquirerPy for arrow-key selection and beautiful prompts.
Texts are loaded from i18n translation files so adding a new language
is just creating a JSON file.
"""

from __future__ import annotations

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from nanobot.cli.i18n import LANGUAGES, t
from nanobot.config.schema import Config

console = Console()

# ---------------------------------------------------------------------------
# Provider metadata
# ---------------------------------------------------------------------------

POPULAR_PROVIDERS: list[str] = [
    "openrouter",
    "anthropic",
    "openai",
    "deepseek",
    "gemini",
    "groq",
    "moonshot",
]

PROVIDER_MODELS: dict[str, list[tuple[str, str]]] = {
    "openrouter": [
        ("anthropic/claude-sonnet-4-5", "⭐ Claude Sonnet 4.5 (recomendado)"),
        ("anthropic/claude-opus-4-5", "🧠 Claude Opus 4.5 (más inteligente)"),
        ("openai/gpt-4o", "🟢 GPT-4o"),
        ("deepseek/deepseek-chat", "🔵 DeepSeek Chat (económico)"),
        ("google/gemini-2.5-pro", "🔷 Gemini 2.5 Pro"),
    ],
    "anthropic": [
        ("anthropic/claude-sonnet-4-5", "⭐ Claude Sonnet 4.5 (recomendado)"),
        ("anthropic/claude-opus-4-5", "🧠 Claude Opus 4.5"),
        ("anthropic/claude-haiku-3-5", "⚡ Claude Haiku 3.5 (rápido)"),
    ],
    "openai": [
        ("openai/gpt-4o", "⭐ GPT-4o (recomendado)"),
        ("openai/gpt-4o-mini", "⚡ GPT-4o Mini (rápido)"),
        ("openai/o1", "🧠 o1 (razonamiento)"),
    ],
    "deepseek": [
        ("deepseek/deepseek-chat", "⭐ DeepSeek Chat (recomendado)"),
        ("deepseek/deepseek-reasoner", "🧠 DeepSeek Reasoner"),
    ],
    "gemini": [
        ("gemini/gemini-2.5-pro", "⭐ Gemini 2.5 Pro (recomendado)"),
        ("gemini/gemini-2.5-flash", "⚡ Gemini 2.5 Flash (rápido)"),
    ],
    "groq": [
        ("groq/llama-3.3-70b-versatile", "⭐ Llama 3.3 70B (recomendado)"),
        ("groq/llama-3.1-8b-instant", "⚡ Llama 3.1 8B (rápido)"),
    ],
    "moonshot": [
        ("moonshot/kimi-k2.5", "⭐ Kimi K2.5 (recomendado)"),
    ],
}

PROVIDER_HELP_URLS: dict[str, str] = {
    "openrouter": "https://openrouter.ai/keys",
    "anthropic": "https://console.anthropic.com/settings/keys",
    "openai": "https://platform.openai.com/api-keys",
    "deepseek": "https://platform.deepseek.com/api_keys",
    "gemini": "https://aistudio.google.com/apikey",
    "groq": "https://console.groq.com/keys",
    "moonshot": "https://platform.moonshot.cn/console/api-keys",
    "minimax": "https://platform.minimaxi.com/user-center/basic-information/interface-key",
    "zhipu": "https://open.bigmodel.cn/usercenter/apikeys",
    "dashscope": "https://dashscope.console.aliyun.com/apiKey",
    "aihubmix": "https://aihubmix.com/token",
    "siliconflow": "https://cloud.siliconflow.cn/account/ak",
}

CHANNEL_ORDER: list[str] = [
    "telegram", "discord", "whatsapp", "email",
    "slack", "feishu", "dingtalk", "qq", "mochat",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mask(value: str) -> str:
    """Mask a secret: 'sk-or-v1-abc123...' → 'sk-or-v1-••••••'."""
    if not value:
        return ""
    visible = min(8, len(value) // 3)
    return value[:visible] + "••••••"


def _is_secret(name: str) -> bool:
    """Check if a field name likely holds a secret."""
    return any(w in name.lower() for w in ("key", "token", "password", "secret"))


def _provider_label(name: str, lang: str) -> str:
    """Get display label for a provider, with i18n fallback."""
    label = t(f"provider_{name}", lang)
    return label if label != f"provider_{name}" else name.replace("_", " ").title()


def _channel_label(name: str, lang: str) -> str:
    """Get display label for a channel, with i18n fallback."""
    label = t(f"channel_{name}", lang)
    return label if label != f"channel_{name}" else name.replace("_", " ").title()


def _section(title: str) -> None:
    """Print a section header with a rule line."""
    console.print()
    console.print(Rule(title, style="yellow"))
    console.print()


# ---------------------------------------------------------------------------
# Step 1: Language
# ---------------------------------------------------------------------------

def _select_language(config: Config) -> str:
    """Arrow-key language selector. Always shown bilingually."""
    console.print(f"{t('lang_prompt')}\n")

    lang_codes = list(LANGUAGES.keys())
    choices = [Choice(value=code, name=LANGUAGES[code]) for code in lang_codes]

    lang = inquirer.select(
        message=t("lang_select"),
        choices=choices,
        default=config.language if config.language in lang_codes else lang_codes[0],
        pointer="❯",
    ).execute()

    config.language = lang
    return lang


# ---------------------------------------------------------------------------
# Step 2: Provider → Model → API Key
# ---------------------------------------------------------------------------

def _select_provider(config: Config, lang: str) -> str | None:
    """Arrow-key provider selection."""
    _section(t("step_provider_title", lang))
    console.print(f"[dim]{t('step_provider_help', lang)}[/dim]\n")

    choices = []
    for name in POPULAR_PROVIDERS:
        label = _provider_label(name, lang)
        prov_cfg = getattr(config.providers, name, None)
        if prov_cfg and prov_cfg.api_key:
            label += " [green]✓[/green]"
        choices.append(Choice(value=name, name=label))

    choices.append(Separator())
    choices.append(Choice(value="__more__", name=t("step_provider_more", lang)))

    result = inquirer.select(
        message=t("select_number", lang),
        choices=choices,
        pointer="❯",
    ).execute()

    if result == "__more__":
        return _select_more_providers(config, lang)
    return result


def _select_more_providers(config: Config, lang: str) -> str | None:
    """Show all non-popular providers from the schema."""
    choices = [Choice(value="__back__", name=t("back", lang))]
    choices.append(Separator())

    for name in config.providers.model_fields:
        if name in POPULAR_PROVIDERS:
            continue
        label = _provider_label(name, lang)
        prov_cfg = getattr(config.providers, name, None)
        if prov_cfg and prov_cfg.api_key:
            label += " [green]✓[/green]"
        choices.append(Choice(value=name, name=label))

    result = inquirer.select(
        message=t("select_number", lang),
        choices=choices,
        pointer="❯",
    ).execute()

    return None if result == "__back__" else result


def _select_model(provider: str, lang: str) -> str:
    """Arrow-key model selector with manual input option."""
    _section(t("step_model_title", lang))
    console.print(f"[dim]{t('step_model_help', lang)}[/dim]\n")

    models = PROVIDER_MODELS.get(provider, [])
    choices = [Choice(value=model_id, name=label) for model_id, label in models]
    choices.append(Separator())
    choices.append(Choice(value="__manual__", name=t("step_model_manual", lang)))

    result = inquirer.select(
        message=t("select_number", lang),
        choices=choices,
        pointer="❯",
    ).execute()

    if result == "__manual__":
        return inquirer.text(
            message=t("step_model_manual_prompt", lang),
            validate=lambda val: len(val.strip()) > 0,
        ).execute()
    return result


def _prompt_api_key(provider: str, lang: str) -> str:
    """Prompt for API key with help URL. Uses secret input."""
    url = PROVIDER_HELP_URLS.get(provider, "")
    _section(t("step_key_title", lang))
    if url:
        console.print(f"[dim]{t('step_key_help', lang, url=url)}[/dim]\n")

    key = inquirer.secret(
        message=t("step_key_prompt", lang),
        validate=lambda val: len(val.strip()) > 0,
    ).execute()

    console.print(f"[green]{t('step_key_success', lang)}[/green]")
    return key


# ---------------------------------------------------------------------------
# Step 3: Channel selection & configuration
# ---------------------------------------------------------------------------

def _select_channel(config: Config, lang: str) -> str | None:
    """Arrow-key channel selector."""
    _section(t("step_channel_title", lang))
    console.print(f"[dim]{t('step_channel_help', lang)}[/dim]\n")

    choices = []
    for name in CHANNEL_ORDER:
        label = _channel_label(name, lang)
        ch_cfg = getattr(config.channels, name, None)
        if ch_cfg and ch_cfg.enabled:
            label += " [green]✓[/green]"
        choices.append(Choice(value=name, name=label))

    choices.append(Separator())
    choices.append(Choice(value="__skip__", name=t("step_channel_skip", lang)))

    result = inquirer.select(
        message=t("select_number", lang),
        choices=choices,
        pointer="❯",
    ).execute()

    return None if result == "__skip__" else result


def _configure_channel(channel_name: str, config: Config, lang: str) -> None:
    """Configure a channel interactively with guided instructions."""
    ch_cfg = getattr(config.channels, channel_name)
    ch_cfg.enabled = True

    if channel_name == "telegram":
        _configure_telegram(ch_cfg, lang)
    elif channel_name == "discord":
        _configure_discord(ch_cfg, lang)
    elif channel_name == "whatsapp":
        _configure_whatsapp(ch_cfg, lang)
    elif channel_name == "slack":
        _configure_slack(ch_cfg, lang)
    else:
        _configure_generic_channel(channel_name, ch_cfg, lang)


def _configure_telegram(ch_cfg: BaseModel, lang: str) -> None:
    """Telegram setup with BotFather guide."""
    console.print()
    console.print(Panel(
        t("telegram_guide", lang),
        title=t("telegram_title", lang),
        border_style="cyan",
        padding=(1, 2),
        expand=False,
    ))
    console.print()

    token = inquirer.secret(
        message=t("telegram_token_prompt", lang),
        validate=lambda val: len(val.strip()) > 0,
    ).execute()
    ch_cfg.token = token
    console.print(f"[green]{t('telegram_token_success', lang)}[/green]\n")

    console.print(f"[dim]{t('telegram_restrict_question', lang)}[/dim]\n")
    restrict = inquirer.confirm(
        message=t("telegram_restrict_prompt", lang),
        default=False,
    ).execute()
    if restrict:
        raw = inquirer.text(
            message=t("telegram_allow_from_prompt", lang),
            default="",
        ).execute()
        ch_cfg.allow_from = [x.strip() for x in raw.split(",") if x.strip()]

    console.print(f"[green]{t('telegram_success', lang)}[/green]")


def _configure_discord(ch_cfg: BaseModel, lang: str) -> None:
    """Discord setup with guide."""
    console.print()
    console.print(Panel(
        t("discord_guide", lang),
        title=t("discord_title", lang),
        border_style="cyan",
        padding=(1, 2),
        expand=False,
    ))
    console.print()

    token = inquirer.secret(
        message=t("discord_token_prompt", lang),
        validate=lambda val: len(val.strip()) > 0,
    ).execute()
    ch_cfg.token = token
    console.print(f"[green]{t('discord_success', lang)}[/green]")


def _configure_whatsapp(ch_cfg: BaseModel, lang: str) -> None:
    """WhatsApp setup with bridge guide."""
    console.print()
    console.print(Panel(
        t("whatsapp_guide", lang),
        title=t("whatsapp_title", lang),
        border_style="cyan",
        padding=(1, 2),
        expand=False,
    ))
    console.print()

    url = inquirer.text(
        message=t("whatsapp_bridge_url_prompt", lang),
        default=ch_cfg.bridge_url,
    ).execute()
    ch_cfg.bridge_url = url

    token = inquirer.text(
        message=t("whatsapp_token_prompt", lang),
        default="",
    ).execute()
    if token:
        ch_cfg.bridge_token = token

    console.print(f"[green]{t('whatsapp_success', lang)}[/green]")


def _configure_slack(ch_cfg: BaseModel, lang: str) -> None:
    """Slack setup with guide."""
    console.print()
    console.print(Panel(
        t("slack_guide", lang),
        title=t("slack_title", lang),
        border_style="cyan",
        padding=(1, 2),
        expand=False,
    ))
    console.print()

    bot_token = inquirer.secret(
        message=t("slack_bot_token_prompt", lang),
        validate=lambda val: len(val.strip()) > 0,
    ).execute()
    ch_cfg.bot_token = bot_token

    app_token = inquirer.secret(
        message=t("slack_app_token_prompt", lang),
        validate=lambda val: len(val.strip()) > 0,
    ).execute()
    ch_cfg.app_token = app_token

    console.print(f"[green]{t('slack_success', lang)}[/green]")


def _configure_generic_channel(name: str, ch_cfg: BaseModel, lang: str) -> None:
    """Generic channel setup — prompts for credential-like fields."""
    title_key = f"{name}_title"
    title = t(title_key, lang)
    if title == title_key:
        title = _channel_label(name, lang)

    guide_key = f"{name}_guide"
    guide = t(guide_key, lang)

    if guide != guide_key:
        console.print()
        console.print(Panel(guide, title=title, border_style="cyan", padding=(1, 2), expand=False))
        console.print()
    else:
        _section(title)

    for field_name in ch_cfg.model_fields:
        if field_name in ("enabled", "allow_from"):
            continue
        current = getattr(ch_cfg, field_name)
        if isinstance(current, str) and _is_secret(field_name):
            label = field_name.replace("_", " ").title()
            val = inquirer.secret(
                message=f"{t('generic_channel_token_prompt', lang)} ({label})",
            ).execute()
            if val:
                setattr(ch_cfg, field_name, val)

    console.print(f"[green]{t('generic_channel_success', lang, name=name.title())}[/green]")


# ---------------------------------------------------------------------------
# Step 4: Standard vs Custom
# ---------------------------------------------------------------------------

def _finish_or_advanced(config: Config, lang: str) -> bool:
    """Arrow-key standard/custom selection."""
    _section(t("step_finish_title", lang))
    console.print(f"[dim]{t('step_finish_help', lang)}[/dim]\n")

    choices = [
        Choice(
            value="standard",
            name=f"{t('step_finish_standard', lang)} — {t('step_finish_standard_desc', lang)}",
        ),
        Choice(
            value="advanced",
            name=f"{t('step_finish_custom', lang)} — {t('step_finish_custom_desc', lang)}",
        ),
    ]

    result = inquirer.select(
        message=t("select_number", lang),
        choices=choices,
        pointer="❯",
    ).execute()

    return result == "advanced"


# ---------------------------------------------------------------------------
# Advanced menu (dynamic Pydantic introspection)
# ---------------------------------------------------------------------------

_BACK = "__back__"


def _advanced_menu(config: Config, lang: str) -> None:
    """Full advanced config menu loop with arrow-key navigation."""
    sections = [
        ("agents", t("advanced_agents", lang)),
        ("providers", t("advanced_providers", lang)),
        ("channels", t("advanced_channels", lang)),
        ("gateway", t("advanced_gateway", lang)),
        ("tools", t("advanced_tools", lang)),
    ]

    while True:
        _section(t("advanced_title", lang))

        choices = [Choice(value=key, name=label) for key, label in sections]
        choices.append(Separator())
        choices.append(Choice(value=_BACK, name=t("advanced_save", lang)))

        result = inquirer.select(
            message=t("select_number", lang),
            choices=choices,
            pointer="❯",
        ).execute()

        if result == _BACK:
            break
        elif result == "providers":
            _advanced_providers(config, lang)
        elif result == "channels":
            _advanced_channels(config, lang)
        elif result == "agents":
            _configure_agent_defaults(config.agents.defaults, lang)
        else:
            section = getattr(config, result)
            _configure_model_fields(result, section, lang)


def _advanced_providers(config: Config, lang: str) -> None:
    """Advanced providers submenu with arrow-key selection."""
    while True:
        choices = [Choice(value=_BACK, name=t("back", lang))]
        choices.append(Separator())

        for name in config.providers.model_fields:
            prov_cfg = getattr(config.providers, name)
            label = _provider_label(name, lang)
            if prov_cfg.api_key:
                label += f" [green]✓[/green] ({_mask(prov_cfg.api_key)})"
            choices.append(Choice(value=name, name=label))

        result = inquirer.select(
            message=t("advanced_providers", lang),
            choices=choices,
            pointer="❯",
        ).execute()

        if result == _BACK:
            break
        prov_cfg = getattr(config.providers, result)
        _configure_model_fields(result, prov_cfg, lang)


def _advanced_channels(config: Config, lang: str) -> None:
    """Advanced channels submenu with arrow-key selection."""
    while True:
        choices = [Choice(value=_BACK, name=t("back", lang))]
        choices.append(Separator())

        for name in config.channels.model_fields:
            ch_cfg = getattr(config.channels, name)
            label = _channel_label(name, lang)
            if ch_cfg.enabled:
                label += " [green]✓[/green]"
            choices.append(Choice(value=name, name=label))

        result = inquirer.select(
            message=t("advanced_channels", lang),
            choices=choices,
            pointer="❯",
        ).execute()

        if result == _BACK:
            break
        ch_cfg = getattr(config.channels, result)
        _configure_model_fields(result, ch_cfg, lang)


def _configure_agent_defaults(defaults: BaseModel, lang: str) -> None:
    """Configure agent defaults with helpful descriptions."""
    console.print()

    field_help = {
        "workspace": ("agent_model_label", "agent_model_help"),
        "model": ("agent_model_label", "agent_model_help"),
        "temperature": ("agent_temperature_label", "agent_temperature_help"),
        "max_tokens": ("agent_max_tokens_label", "agent_max_tokens_help"),
        "max_tool_iterations": ("agent_max_iterations_label", "agent_max_iterations_help"),
        "memory_window": ("agent_memory_window_label", "agent_memory_window_help"),
    }

    for field_name in defaults.model_fields:
        current = getattr(defaults, field_name)
        label_key, help_key = field_help.get(field_name, (None, None))
        label = t(label_key, lang) if label_key else field_name.replace("_", " ").title()
        help_text = t(help_key, lang) if help_key else ""

        if help_text:
            console.print(f"[dim]{help_text}[/dim]")

        new_val = _prompt_field(label, type(current), current, lang)
        if new_val != current:
            setattr(defaults, field_name, new_val)


def _configure_model_fields(name: str, model: BaseModel, lang: str) -> None:
    """Dynamically configure all fields of a Pydantic model."""
    console.print(f"\n[bold]{name.replace('_', ' ').title()}[/bold]")

    for field_name, field_info in model.model_fields.items():
        current = getattr(model, field_name)
        annotation = field_info.annotation

        if isinstance(current, BaseModel):
            _configure_model_fields(field_name, current, lang)
            continue

        if isinstance(current, dict):
            continue

        label = field_name.replace("_", " ").title()
        new_val = _prompt_field(label, annotation, current, lang, is_secret=_is_secret(field_name))
        if new_val != current:
            setattr(model, field_name, new_val)


def _prompt_field(
    label: str,
    annotation: type,
    current: object,
    lang: str,
    is_secret: bool = False,
) -> object:
    """Prompt for a single field value using InquirerPy."""
    if annotation is bool or annotation == bool:
        return inquirer.confirm(message=label, default=current).execute()

    if annotation is int:
        raw = inquirer.number(
            message=label,
            default=current,
            float_allowed=False,
        ).execute()
        return int(raw)

    if annotation is float:
        raw = inquirer.number(
            message=label,
            default=current,
            float_allowed=True,
        ).execute()
        return float(raw)

    # list[str]
    if annotation == list[str] or (hasattr(annotation, "__origin__") and getattr(annotation, "__origin__", None) is list):
        current_str = ", ".join(current) if current else ""
        console.print(f"[dim]{t('field_list_help', lang)}[/dim]")
        raw = inquirer.text(message=label, default=current_str).execute()
        if not raw or not raw.strip():
            return []
        return [x.strip() for x in raw.split(",") if x.strip()]

    # str / str | None
    if is_secret and current:
        display = _mask(current)
        console.print(f"[dim]{t('field_secret_keep', lang)}[/dim]")
        raw = inquirer.text(message=label, default=display).execute()
        if raw == display:
            return current
        return raw
    elif is_secret:
        raw = inquirer.secret(message=label).execute()
        return raw
    else:
        default = current if current is not None else ""
        raw = inquirer.text(message=label, default=str(default)).execute()
        if raw == "" and "None" in str(annotation):
            return None
        return raw


# ---------------------------------------------------------------------------
# Main wizard entry point
# ---------------------------------------------------------------------------

def config_wizard(config: Config) -> Config:
    """🍌 Run the full Banabot configuration wizard.

    Guides the user through: language → provider → model → API key → channel.
    Returns the modified config (caller is responsible for saving).
    """
    console.print()
    console.print(Rule("[bold yellow]banabot config[/bold yellow]", style="yellow"))
    console.print()

    # Step 1: Language
    lang = _select_language(config)

    # Step 2: Provider → Model → API Key
    provider = _select_provider(config, lang)
    if provider:
        model = _select_model(provider, lang)
        config.agents.defaults.model = model

        from nanobot.providers.registry import find_by_name
        spec = find_by_name(provider)
        if spec and spec.is_oauth:
            console.print(f"[dim]{provider} uses OAuth — no API key needed.[/dim]")
        else:
            key = _prompt_api_key(provider, lang)
            prov_cfg = getattr(config.providers, provider)
            prov_cfg.api_key = key

    # Step 3: Channel
    channel = _select_channel(config, lang)
    if channel:
        _configure_channel(channel, config, lang)

    # Step 4: Standard or Custom?
    wants_advanced = _finish_or_advanced(config, lang)
    if wants_advanced:
        _advanced_menu(config, lang)

    console.print()
    console.print(Rule(style="green"))
    console.print(f"[green]{t('step_finish_done', lang)}[/green]")
    console.print()
    return config
