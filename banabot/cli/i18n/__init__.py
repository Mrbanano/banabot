"""🍌 Banabot i18n — translation system for the interactive wizard.

To add a new language:
  1. Copy es.json → <lang_code>.json and translate
  2. Add the language code + label to LANGUAGES below
  3. Done — the wizard will show it automatically
"""

import json
from pathlib import Path

# Available languages: code → display label
# Using ISO 3166-1 alpha-2 codes with terminal-safe styling
LANGUAGES: dict[str, str] = {
    "es": "[magenta]ES[/] Español",
    "en": "[cyan]EN[/] English",
}

_I18N_DIR = Path(__file__).parent
_cache: dict[str, dict[str, str]] = {}


def _load(lang: str) -> dict[str, str]:
    """Load translation file for a language. Cached after first load."""
    if lang not in _cache:
        path = _I18N_DIR / f"{lang}.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                _cache[lang] = json.load(f)
        else:
            _cache[lang] = {}
    return _cache[lang]


def t(key: str, lang: str = "es", **kwargs: str) -> str:
    """Translate a key. Falls back to Spanish if not found in the target language.

    Supports {placeholder} formatting via kwargs.
    """
    translations = _load(lang)
    fallback = _load("es")
    text = translations.get(key) or fallback.get(key) or key
    if kwargs:
        text = text.format(**kwargs)
    return text
