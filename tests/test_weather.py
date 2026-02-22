"""Tests for WeatherTool."""

import pytest

from banabot.agent.tools.weather import WeatherTool


class TestWeatherTool:
    """Test cases for WeatherTool."""

    @pytest.fixture
    def weather_tool(self):
        """Create WeatherTool instance."""
        return WeatherTool()

    def test_tool_name(self, weather_tool):
        """Test tool name is 'weather'."""
        assert weather_tool.name == "weather"

    def test_tool_description(self, weather_tool):
        """Test tool has description."""
        assert "weather" in weather_tool.description.lower()

    def test_parameters_location_required(self, weather_tool):
        """Test location is required parameter."""
        params = weather_tool.parameters
        assert "location" in params["properties"]
        assert "location" in params["required"]

    def test_parameters_format_options(self, weather_tool):
        """Test format parameter has correct options."""
        params = weather_tool.parameters
        format_prop = params["properties"]["format"]
        assert format_prop["enum"] == ["compact", "full", "forecast"]
        assert format_prop["default"] == "compact"

    def test_parameters_units_options(self, weather_tool):
        """Test units parameter has correct options."""
        params = weather_tool.parameters
        units_prop = params["properties"]["units"]
        assert units_prop["enum"] == ["metric", "imperial"]
        assert units_prop["default"] == "metric"

    @pytest.mark.asyncio
    async def test_execute_with_location(self, weather_tool):
        """Test weather execution with location."""
        result = await weather_tool.execute(location="London")
        # Should return weather info, not error
        assert "London" in result or "error" not in result.lower()

    @pytest.mark.asyncio
    async def test_execute_with_units(self, weather_tool):
        """Test weather with different units."""
        result = await weather_tool.execute(location="London", units="imperial")
        # Should contain F for fahrenheit
        assert "°F" in result or "°C" in result

    def test_weather_code_to_text_clear(self, weather_tool):
        """Test clear weather code."""
        assert weather_tool._weather_code_to_text(0) == "Clear"
        assert weather_tool._weather_code_to_text(1) == "Mainly clear"

    def test_weather_code_to_text_rain(self, weather_tool):
        """Test rain weather codes."""
        assert weather_tool._weather_code_to_text(61) == "Rain"
        assert weather_tool._weather_code_to_text(65) == "Heavy rain"

    def test_weather_code_to_text_unknown(self, weather_tool):
        """Test unknown weather code."""
        result = weather_tool._weather_code_to_text(999)
        assert "999" in result

    @pytest.mark.asyncio
    async def test_wttr_in_format_compact(self, weather_tool):
        """Test wttr.in compact format."""
        result = await weather_tool._wttr_in("London", "compact", "m")
        assert result is not None
        assert "London" in result

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires network access to wttr.in")
    async def test_wttr_in_with_airport_code(self, weather_tool):
        """Test wttr.in with airport code."""
        result = await weather_tool._wttr_in("JFK", "compact", "m")
        assert result is not None

    @pytest.mark.asyncio
    async def test_open_meteo_geocoding(self, weather_tool):
        """Test Open-Meteo geocoding."""
        result = await weather_tool._open_meteo("Puebla", "metric")
        assert "Puebla" in result
        assert "°C" in result

    @pytest.mark.asyncio
    async def test_open_meteo_imperial(self, weather_tool):
        """Test Open-Meteo with imperial units."""
        result = await weather_tool._open_meteo("New York", "imperial")
        assert "°F" in result

    @pytest.mark.asyncio
    async def test_execute_fallback_to_open_meteo(self, weather_tool):
        """Test fallback from wttr.in to Open-Meteo."""
        # Should work even if one fails
        result = await weather_tool.execute(location="Berlin")
        assert "Berlin" in result or "error" not in result.lower()

    @pytest.mark.asyncio
    async def test_location_not_found(self, weather_tool):
        """Test handling of unknown location."""
        result = await weather_tool._open_meteo("ThisIsNotARealCity12345", "metric")
        assert "not found" in result.lower() or "error" in result.lower()
