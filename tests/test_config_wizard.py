from typer.testing import CliRunner

from banabot.cli.commands import app
from banabot.cli.config_wizard import (
    MODEL_SPECS,
    TEMPERATURE_PRESETS,
    _get_model_specs,
)

runner = CliRunner()


class TestModelSpecs:
    """Tests for MODEL_SPECS configuration."""

    def test_model_specs_contains_expected_models(self):
        """Verify MODEL_SPECS contains all major models."""
        expected_models = [
            "anthropic/claude-opus-4-5",
            "anthropic/claude-sonnet-4-5",
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "deepseek/deepseek-chat",
            "google/gemini-2.5-pro",
            "gemini/gemini-2.5-flash",
        ]

        for model in expected_models:
            assert model in MODEL_SPECS, f"Missing model: {model}"

    def test_model_specs_have_required_fields(self):
        """Verify each model spec has max_context and max_tokens."""
        for model, spec in MODEL_SPECS.items():
            assert "max_context" in spec, f"Missing max_context for {model}"
            assert "max_tokens" in spec, f"Missing max_tokens for {model}"
            assert isinstance(spec["max_context"], int), f"max_context should be int for {model}"
            assert isinstance(spec["max_tokens"], int), f"max_tokens should be int for {model}"

    def test_model_specs_tokens_are_reasonable(self):
        """Verify max_tokens is always less than max_context."""
        for model, spec in MODEL_SPECS.items():
            assert spec["max_tokens"] < spec["max_context"], (
                f"max_tokens should be less than max_context for {model}"
            )

    def test_claude_opus_has_high_tokens(self):
        """Claude Opus should have high token limits (200K context)."""
        spec = MODEL_SPECS["anthropic/claude-opus-4-5"]
        assert spec["max_context"] >= 200000
        assert spec["max_tokens"] >= 50000

    def test_deepseek_has_appropriate_tokens(self):
        """DeepSeek should have appropriate token limits (64K context)."""
        spec = MODEL_SPECS["deepseek/deepseek-chat"]
        assert spec["max_context"] >= 64000
        assert spec["max_tokens"] >= 20000

    def test_gemini_pro_has_high_tokens(self):
        """Gemini 2.5 Pro should have very high token limits (1M context)."""
        spec = MODEL_SPECS["gemini/gemini-2.5-pro"]
        assert spec["max_context"] >= 1000000
        assert spec["max_tokens"] >= 80000


class TestTemperaturePresets:
    """Tests for TEMPERATURE_PRESETS configuration."""

    def test_temperature_presets_contain_all_options(self):
        """Verify all temperature presets are defined."""
        expected = ["creative", "balanced", "concise"]
        for preset in expected:
            assert preset in TEMPERATURE_PRESETS, f"Missing preset: {preset}"

    def test_temperature_presets_have_label_and_value(self):
        """Verify each preset has label (str) and value (float)."""
        for preset, (label, value) in TEMPERATURE_PRESETS.items():
            assert isinstance(label, str), f"Label should be str for {preset}"
            assert isinstance(value, float), f"Value should be float for {preset}"
            assert 0.0 <= value <= 2.0, f"Temperature should be 0-2 for {preset}"

    def test_creative_temperature_is_high(self):
        """Creative should have high temperature (more random)."""
        assert TEMPERATURE_PRESETS["creative"][1] >= 0.7

    def test_balanced_temperature_is_middle(self):
        """Balanced should have middle temperature."""
        assert 0.3 <= TEMPERATURE_PRESETS["balanced"][1] <= 0.5

    def test_concise_temperature_is_low(self):
        """Concise should have low temperature (more deterministic)."""
        assert TEMPERATURE_PRESETS["concise"][1] <= 0.3


class TestGetModelSpecs:
    """Tests for _get_model_specs helper function."""

    def test_exact_match_returns_spec(self):
        """Exact model ID should return correct spec."""
        spec = _get_model_specs("anthropic/claude-opus-4-5")
        assert spec["max_tokens"] == 80000

    def test_partial_match_returns_spec(self):
        """Partial match (e.g., 'gpt-4o' in model string) should work."""
        spec = _get_model_specs("openai/gpt-4o")
        assert "max_tokens" in spec

    def test_unknown_model_returns_defaults(self):
        """Unknown model should return sensible defaults."""
        spec = _get_model_specs("unknown/model-xyz")
        assert spec["max_context"] == 32000
        assert spec["max_tokens"] == 16000

    def test_case_insensitive_match(self):
        """Match should be case insensitive."""
        spec1 = _get_model_specs("anthropic/CLAUDE-OPUS-4-5")
        spec2 = _get_model_specs("anthropic/claude-opus-4-5")
        assert spec1 == spec2


class TestConfigWizardCLI:
    """Integration tests for config wizard CLI flow."""

    def test_onboard_command_exists(self):
        """Verify onboard command is registered."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "onboard" in result.stdout

    def test_status_command_works(self):
        """Verify status command works."""
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
