"""Weather tool using wttr.in and Open-Meteo."""

import urllib.parse
from typing import Any

import httpx

from banabot.agent.tools.base import Tool


class WeatherTool(Tool):
    """Get current weather and forecasts using wttr.in or Open-Meteo."""

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return """Get current weather and forecasts for any location.
- Uses wttr.in for quick weather info
- Supports cities, airport codes (JFK), or coordinates
- Returns temperature, conditions, humidity, wind"""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, airport code, or coordinates (e.g., 'Puebla', 'JFK', '19.04,-98.20')",
                },
                "format": {
                    "type": "string",
                    "enum": ["compact", "full", "forecast"],
                    "default": "compact",
                    "description": "Output format",
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial"],
                    "default": "metric",
                    "description": "Temperature units",
                },
            },
            "required": ["location"],
        }

    async def execute(
        self,
        location: str,
        format: str = "compact",  # noqa: A002
        units: str = "metric",
        **kwargs: Any,
    ) -> str:
        """Execute weather lookup."""
        unit_flag = "m" if units == "metric" else "u"

        # Try wttr.in first
        try:
            result = await self._wttr_in(location, format, unit_flag)
            if result:
                return result
        except Exception:
            pass

        # Fallback to Open-Meteo
        try:
            return await self._open_meteo(location, units)
        except Exception as e:
            return f"Error getting weather: {str(e)}"

    async def _wttr_in(self, location: str, fmt: str, unit: str) -> str | None:
        """Get weather from wttr.in."""
        encoded = urllib.parse.quote(location)

        if fmt == "full":
            url = f"wttr.in/{encoded}?T&{unit}"
        elif fmt == "forecast":
            url = f"wttr.in/{encoded}?{unit}"
        else:  # compact
            url = f"wttr.in/{encoded}?format=%l:+%c+%t+%h+%w&{unit}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"https://{url}")
            if resp.status_code == 200:
                return resp.text.strip()
        return None

    async def _open_meteo(self, location: str, units: str) -> str:
        """Get weather from Open-Meteo (fallback)."""
        # First geocode
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(location)}&count=1"

        async with httpx.AsyncClient(timeout=10.0) as client:
            geo_resp = await client.get(geo_url)
            geo_data = geo_resp.json()

            if not geo_data.get("results"):
                return f"Location not found: {location}"

            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            name = geo_data["results"][0]["name"]

            # Get weather
            unit_sys = "celsius" if units == "metric" else "fahrenheit"
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current_weather=true"
                f"&temperature_unit={unit_sys}"
            )

            weather_resp = await client.get(weather_url)
            weather = weather_resp.json()["current_weather"]

            temp = weather["temperature"]
            wind = weather["windspeed"]
            code = weather["weathercode"]
            condition = self._weather_code_to_text(code)

            return (
                f"{name}: {condition}, {temp}°{'C' if units == 'metric' else 'F'}, wind {wind} km/h"
            )

    def _weather_code_to_text(self, code: int) -> str:
        """Convert WMO weather code to text."""
        codes = {
            0: "Clear",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Drizzle",
            55: "Dense drizzle",
            61: "Rain",
            63: "Rain",
            65: "Heavy rain",
            71: "Snow",
            73: "Snow",
            75: "Heavy snow",
            80: "Rain showers",
            81: "Rain showers",
            82: "Violent showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
        }
        return codes.get(code, f"Code {code}")
