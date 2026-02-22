# Tarea Unificada: Sistema de Clima

## Objetivo
El bot debe poder obtener el clima correctamente preguntando la ubicación del usuario.

## Requerimientos

### 1. WeatherTool Nativa (Tarea 6)
- **Estado:** ❌ PENDIENTE
- **Descripción:** Crear tool nativa que use wttr.in y Open-Meteo
- **Archivo:** `src/banabot/agent/tools/weather.py`
- **Código:** Ya está escrito en tareas.md (líneas 133-286)

### 2. Registrar WeatherTool (Tarea 6)
- **Estado:** ❌ PENDIENTE
- **Descripción:** Registrar la tool en loop.py
- **Código:** Ya está escrito en tareas.md (líneas 290-294)

### 3. Confirmar Ubicación para Clima (Tarea 11)
- **Estado:** ❌ PENDIENTE
- **Descripción:** Antes de usar weather, confirmar ubicación
- **Código:** Ya está escrito en tareas.md (líneas 400-419)
- **Lógica:**
  - Si NO tiene location → preguntar "¿En qué ciudad estás?"
  - Si SÍ tiene location → confirmar "¿Sigues en {location}?"

### 4. Instrucciones de Location (Tarea 8)
- **Estado:** ❌ PENDIENTE
- **Descripción:** Agregar instrucciones de location awareness al prompt
- **Código:** Ya está escrito en tareas.md (líneas 338-351)

---

## Implementación

### Paso 1: Crear WeatherTool
Crear archivo `src/banabot/agent/tools/weather.py` con el código de tareas.md

### Paso 2: Registrar en loop.py
```python
from banabot.agent.tools.weather import WeatherTool
self.tools.register(WeatherTool())
```

### Paso 3: Agregar Location Confirmation al prompt
```python
## Location Confirmation (CRITICAL)
Before getting weather or distances, you MUST check if you know the user's location:

1. If user_fields.location is UNKNOWN:
   → Ask "¿Me recuerdas dónde estás?" or "¿En qué ciudad estás?"

2. If user_fields.location EXISTS (e.g., "Puebla, México"):
   → Ask confirmation: "¿Sigues en {location}?" before using weather/distance tools
   → Wait for user confirmation before proceeding
```

---

## Criterios de Éxito

- [ ] El usuario pregunta "¿Qué clima hace?" → Bot pregunta ubicación
- [ ] El usuario da ubicación → Bot la guarda en profile
- [ ] Conversación siguiente → Bot confirma "¿Sigues en X?"
- [ ] El bot usa `weather` tool (no web_search) para clima
- [ ] El bot responde con temperatura real (no links)

---

## Notas

- La tarea 5 (Weather Skill como Always) ya no es necesaria si creamos la tool nativa
- La tarea 7 (Location en profile) ya funciona - el LLM lo hace automáticamente
