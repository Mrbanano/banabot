# Tareas - BanaBot Fixes

## Tarea 1: Agregar Honesty Rule al System Prompt
**Prioridad:** 🔴 ALTA  
**Archivo:** `src/banabot/agent/context.py`  
**Líneas aprox:** 130-140

### Descripción
El agente miente sobre usar herramientas. Agregar instrucción explícita de transparencia.

### Cambios:
```python
# En _get_identity(), agregar después de línea 138:
"""
## Honesty Rule
If you use ANY tool, ALWAYS be transparent about it.
NEVER say "no usé herramientas" or "no usé ninguna herramienta" when you did.
Example: "Usé web_search para buscar el clima de Puebla"
"""
```

### Criterio de éxito:
- El bot NUNCA dice "no usé herramientas" cuando sí las usó

---

## Tarea 2: Agregar Learning Rule al System Prompt
**Prioridad:** 🔴 ALTA  
**Archivo:** `src/banabot/agent/context.py`  
**Líneas aprox:** 140-150

### Descripción
El agente no sabe que DEBE guardar preferencias del usuario en el profile.

### Cambios:
```python
# Agregar después de Honesty Rule:
"""
## Learning Rule
When you learn something important about the user:
IMMEDIATELY use: profile action=set_user_field key=X value=Y

Examples:
- "Tengo un perro salchicha" → profile action=set_user_field key=pet value="perro salchicha"
- "Vivo en Puebla" → profile action=set_user_field key=location value="Puebla, México"
- "Me gusta el fútbol" → profile action=set_user_field key=interests value="fútbol"
"""
```

### Criterio de éxito:
- Después de mencionar información personal, el bot usa profile tool

---

## Tarea 3: Arreglar Consolidación de Memoria
**Prioridad:** 🔴 ALTA  
**Archivo:** `src/banabot/agent/loop.py`  
**Líneas aprox:** 342-344

### Descripción
La consolidación de memoria solo se dispara cuando hay 50+ mensajes. En conversaciones cortas nunca ocurre.

### Cambios:
```python
# En _process_message(), cambiar:
if len(session.messages) > self.memory_window:
# A:
if len(session.messages) >= 3:  # Consolidar cada 3+ mensajes

# O mejor: always consolidate at end of session
# Agregar al final de _process_message(), antes del return:
if len(session.messages) >= 3:
    asyncio.create_task(self._consolidate_memory(session))
```

### Criterio de éxito:
- MEMORY.md contiene información después de 3+ intercambios

---

## Tarea 4: Reducir memory_window
**Prioridad:** 🟡 MEDIA  
**Archivo:** `src/banabot/agent/loop.py`  
**Líneas aprox:** ~90

### Descripción
El memory_window actual de 50 es muy alto.

### Cambios:
```python
# En __init__ de AgentLoop, cambiar:
self.memory_window = 50
# A:
self.memory_window = 10
```

---

## Tarea 5: Marcar Weather Skill como Always
**Prioridad:** 🟡 MEDIA  
**Archivo:** `src/banabot/skills/weather/SKILL.md`  
**Líneas:** 1-7

### Descripción
El skill de weather existe pero el agente no lo usa porque no está marcado como "always".

### Cambios:
```yaml
---
name: weather
description: Get current weather and forecasts (no API key required).
metadata: {"nanobot":{"emoji":"🌤️","requires":{"bins":["curl"]},"always":true}}
---
```

### Criterio de éxito:
- El weather skill se carga en el contexto inicial del agente

---

## Tarea 6: Crear WeatherTool Nativa (COMPLETA)
**Prioridad:** 🔴 ALTA  
**Archivo:** `src/banabot/agent/tools/weather.py` (CREAR)  
**Registrar en:** `src/banabot/agent/loop.py`

### Descripción
Convertir el skill de weather en una tool nativa. El skill actual usa:
- **wttr.in** (principal): `curl -s "wttr.in/London?format=3"` → `London: ⛅️ +8°C`
- **Open-Meteo** (fallback JSON): API gratuita sin key

### Implementación completa:

```python
# src/banabot/agent/tools/weather.py
"""Weather tool using wttr.in and Open-Meteo."""

import json
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
        except Exception as e:
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
            
            return f"{name}: {condition}, {temp}°{'C' if units == 'metric' else 'F'}, wind {wind} km/h"

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
```

### Registrar en loop.py:

```python
# En loop.py, línea ~120, después de otros registros:
from banabot.agent.tools.weather import WeatherTool
self.tools.register(WeatherTool())
```

### Criterio de éxito:
- `weather` tool registrada y disponible
- El agente usa `weather` en vez de `web_search` para preguntas de clima
- Respuesta en formato legible (no raw JSON)

---

## Tarea 7: Agregar Location al Profile
**Prioridad:** 🟡 MEDIA  
**Archivo:** `src/banabot/agent/tools/profile.py`  
**Líneas aprox:** 50-60

### Descripción
El profile tool no tiene el campo `location` disponible.

### Cambios:
```python
# En parameters, agregar a key enum:
"location"
```

### Además, en context.py:
```python
# Inferir ubicación del timezone
timezone = profile.get("cli_config", {}).get("timezone", "")
if timezone and not profile.get("user_fields", {}).get("location"):
    # America/New_York → probablemente es México
    if timezone == "America/New_York":
        # Asumir México si el idioma es español
        pass
```

---

## Tarea 8: Agregar Instructions para Location
**Prioridad:** 🟡 MEDIA  
**Archivo:** `src/banabot/agent/context.py`

### Descripción
Instruir al agente quepregunte la ubicación si no la conoce.

### Cambios:
```python
# Agregar al system prompt:
"""
## Location Awareness
If you don't know the user's location:
- Ask: "¿En qué ciudad estás?" or "¿Dónde vives?"
- Save with: profile action=set_user_field key=location value="X"

Use the user's location for:
- Weather queries
- Local searches (restaurants, events, etc.)
- Timezone-aware reminders
"""
```

---

## Tarea 9: Agregar año actual a búsquedas
**Prioridad:** 🟢 BAJA  
**Archivo:** `src/banabot/agent/context.py`

### Descripción
Las búsquedas devuelven resultados desactualizados.

### Cambios:
```python
# En _get_identity(), agregar tip:
"""
When searching for current events, sports scores, or news:
Include the current year (2026) in your search query.
"""
```

---

## Tarea 10: Confirmación de Acciones
**Prioridad:** 🟢 BAJA  
**Archivo:** `src/banabot/agent/context.py`

### Descripción
El bot debe confirmar cuando guarda algo en memoria o profile.

### Cambios:
```python
# Agregar al system prompt:
"""
## Confirmation
After using profile or memory tools, briefly confirm what was saved.
Example: "✅ Guardé que tienes un perro salchicha"
```

---

## Tarea 11: Solicitar Ubicación para Clima/Distancias
**Prioridad:** 🔴 ALTA  
**Archivo:** `src/banabot/agent/context.py`

### Descripción
Antes de obtener clima o distancias, el agente debe verificar si conoce la ubicación del usuario.

### Instrucciones a agregar en el system prompt:

```python
"""
## Location Confirmation (CRITICAL)
Before getting weather or distances, you MUST check if you know the user's location:

1. If user_fields.location is UNKNOWN:
   → Ask "¿Me recuerdas dónde estás?" or "¿En qué ciudad estás?"

2. If user_fields.location EXISTS (e.g., "Puebla, México"):
   → Ask confirmation: "¿Sigues en {location}?" before using weather/distance tools
   → Wait for user confirmation before proceeding

Example conversation:
- User: "¿Qué clima hace?"
- Bot: "¿Sigues en Puebla, México?" (wait for "sí" or "si")

NEVER assume the user's location without asking or confirming.
This applies to: weather, distance calculations, local searches, timezone reminders.
"""
```

### Criterio de éxito:
- El bot pregunta ubicación ANTES de usar weather tool
- Si ya tiene location, confirma "¿Sigues en X?"

---

## Orden de Implementación Sugerida

1. 🔴 Tarea 1 (Honesty Rule) - HOTFIX
2. 🔴 Tarea 2 (Learning Rule) - HOTFIX  
3. 🔴 Tarea 3 (Consolidación) - CRÍTICO
4. 🔴 Tarea 11 (Location Confirmation) - CRÍTICO
5. 🟡 Tarea 6 (WeatherTool nativa) - IMPORTANTE
6. 🟡 Tarea 4 (memory_window)
7. 🟡 Tarea 5 (Weather always)
8. 🟡 Tarea 7-8 (Location)
9. 🟢 Tarea 9-10 (Mejoras)

---

*Documento de tareas generado automáticamente*
