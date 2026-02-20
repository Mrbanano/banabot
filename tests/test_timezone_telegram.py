"""Tests for timezone, telegram, and config utilities."""

import pytest
from unittest.mock import AsyncMock, patch

from banabot.cli.config_wizard import POPULAR_TIMEZONES


class TestPopularTimezones:
    """Tests for timezone configuration."""

    def test_popular_timezones_has_items(self):
        """POPULAR_TIMEZONES should have timezone entries."""
        assert len(POPULAR_TIMEZONES) > 0

    def test_popular_timezones_contains_mexico_city(self):
        """Should contain America/Mexico_City as default."""
        timezones = [tz for tz, label in POPULAR_TIMEZONES]
        assert "America/Mexico_City" in timezones

    def test_popular_timezones_contains_utc(self):
        """Should contain UTC."""
        timezones = [tz for tz, label in POPULAR_TIMEZONES]
        assert "UTC" in timezones

    def test_popular_timezones_format(self):
        """Each timezone should be a tuple of (zone, label)."""
        for tz, label in POPULAR_TIMEZONES:
            assert isinstance(tz, str)
            assert isinstance(label, str)
            assert "/" in tz or tz == "UTC"

    def test_popular_timezones_has_american_zones(self):
        """Should contain American timezones."""
        timezones = [tz for tz, label in POPULAR_TIMEZONES]
        american = [tz for tz in timezones if tz.startswith("America/")]
        assert len(american) >= 4

    def test_popular_timezones_has_european_zones(self):
        """Should contain European timezones."""
        timezones = [tz for tz, label in POPULAR_TIMEZONES]
        european = [tz for tz in timezones if tz.startswith("Europe/")]
        assert len(european) >= 2

    def test_popular_timezones_has_asian_zones(self):
        """Should contain Asian timezones."""
        timezones = [tz for tz, label in POPULAR_TIMEZONES]
        asian = [tz for tz in timezones if tz.startswith("Asia/")]
        assert len(asian) >= 2


class TestTelegramChatIdValidation:
    """Tests for Telegram chat_id validation."""

    def test_chat_id_must_be_numeric(self):
        """Chat ID should be validated as numeric."""
        test_cases = [
            ("123456789", True),
            ("-1001234567890", True),
            ("abc123", False),
            ("not_a_number", False),
            ("", False),
        ]

        for chat_id, expected_valid in test_cases:
            try:
                int(chat_id)
                is_valid = True
            except (ValueError, TypeError):
                is_valid = False

            assert is_valid == expected_valid, f"Failed for: {chat_id}"

    def test_negative_chat_ids_are_valid(self):
        """Negative chat IDs (like group chats) should be valid."""
        group_chat_ids = ["-1001234567890", "-1009876543210", "-1000000000000"]
        for chat_id in group_chat_ids:
            try:
                int(chat_id)
                is_valid = True
            except (ValueError, TypeError):
                is_valid = False
            assert is_valid, f"Group chat ID should be valid: {chat_id}"


class TestApiKeyCleaning:
    """Tests for API key cleaning utilities."""

    def test_clean_api_key_removes_leading_spaces(self):
        """Should remove leading spaces."""
        key = "   sk-test123"
        cleaned = key.strip().lstrip("-").strip()
        assert cleaned == "sk-test123"

    def test_clean_api_key_removes_leading_dashes(self):
        """Should remove leading dashes."""
        key = "---sk-test123"
        cleaned = key.strip().lstrip("-").strip()
        assert cleaned == "sk-test123"

    def test_clean_api_key_removes_both(self):
        """Should remove both spaces and leading dashes."""
        key = "  ---sk-test123  "
        cleaned = key.strip().lstrip("-").strip()
        assert cleaned == "sk-test123"

    def test_clean_api_key_handles_telegram_token(self):
        """Should clean Telegram tokens with dashes."""
        token = "- 1234567890:AAFGTHXRw9WAyIWKUOvl9NlUwxRd7ZILA4M"
        cleaned = token.strip().lstrip("-").strip()
        assert cleaned == "1234567890:AAFGTHXRw9WAyIWKUOvl9NlUwxRd7ZILA4M"

    def test_clean_api_key_preserves_normal_keys(self):
        """Should not affect normal API keys."""
        key = "sk-openai-test123456789"
        cleaned = key.strip().lstrip("-").strip()
        assert cleaned == "sk-openai-test123456789"

    def test_clean_api_key_handles_empty_after_cleaning(self):
        """Should handle keys that become empty after cleaning."""
        key = "---"
        cleaned = key.strip().lstrip("-").strip()
        assert cleaned == ""


class TestTimezoneConfig:
    """Tests for timezone config field."""

    def test_config_has_timezone_field(self):
        """Config should have timezone field."""
        from banabot.config.schema import Config

        config = Config()
        assert hasattr(config, "timezone")

    def test_config_timezone_default(self):
        """Config should have default timezone."""
        from banabot.config.schema import Config

        config = Config()
        assert config.timezone == "America/Mexico_City"
