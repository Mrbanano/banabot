# Plan de Análisis - BanaBot Evals

**Fecha:** 21 de febrero 2026  
**Evaluación:** Primera conversación con Mrbanano  
**Calificación:** 3/10

---

## Resumen Ejecutivo

El bot tiene funcionalidades básicas pero falla en funciones críticas de un agente personal autónomo:
- ❌ Memoria persistente rota
- ❌ Mentira sobre uso de herramientas
- ❌ Sin contexto geográfico
- ❌ No usa herramientas especializadas (weather)
- ❌ No enriquece profile con preferencias

---

## Análisis de Evidencias

### Evidencia 1: evaluacion_banabot_v1.md
| Problema | Severidad | Root Cause |
|----------|-----------|------------|
| MEMORY.md vacío | 🔴 CRÍTICO | Consolidación no se dispara (memory_window=50) |
| HISTORY.md vacío | 🔴 CRÍTICO | Mismo que arriba |
| "No usé herramientas" | 🔴 CRÍTICO | Prompt no incluye transparencia |
| Clima NY en vez de Puebla | 🟡 IMPORTANTE | Falta location en profile |
| Brave误会Browser | 🟡 IMPORTANTE | Falta contexto en prompt |

### Evidencia 2: EVALUACION_PRIMERA_CONVERSACION.md
| Problema | Severidad | Root Cause |
|----------|-----------|------------|
| profile.json sin user_fields | 🔴 CRÍTICO | Agente no sabe que DEBE guardar |
| weather skill no usado | 🟡 IMPORTANTE | Skill no está marcado como "always" |
| Cron sin contexto | 🟡 IMPORTANTE | Falta metadata en recordatorios |

---

## Arquitectura Actual

```
src/banabot/
├── agent/
│   ├── loop.py          # Lógica del agente - USA
│   ├── context.py      # Construye prompts - USA
│   ├── memory.py       # MemoryStore (MEMORY.md) - USA
│   ├── skills.py       # SkillsLoader - USA
│   └── tools/
│       ├── profile.py  # ProfileTool - USA
│       ├── web.py      # WebSearchTool - USA
│       └── cron.py     # CronTool
├── session/
│   └── manager.py      # SessionManager
└── skills/
    └── weather/SKILL.md  # Existe pero no se usa
```

---

## Código a Tocar

### PRIORIDAD 1: Memoria Persistente 🔴

**Archivo:** `src/banabot/agent/loop.py`

**Problema:** 
- `memory_window` default es 50 mensajes
- Consolidación solo se dispara cuando `len(session.messages) > self.memory_window`
- En conversaciones cortas (10-20 msgs) NUNCA se dispara

**Solución:**
```python
# Opción A: Reducir memory_window a 10
self.memory_window = 10

# Opción B (MEJOR): Consolidar al final de cada sesión
# En _process_message(), después de session.save():
asyncio.create_task(self._consolidate_memory(session))
```

**Además:** El agente no sabe que debe guardar hechos importantes en MEMORY.md
- Faltan instrucciones explícitas en el system prompt

---

### PRIORIDAD 2: Transparencia de Herramientas 🔴

**Archivo:** `src/banabot/agent/context.py`

**Problema:** El agente miente sobre usar herramientas

**Solución:** Agregar al system prompt:
```
## Honesty Rule
If you use ANY tool, NEVER say "no usé herramientas" or "no usé ninguna herramienta".
ALWAYS be transparent: "Usé web_search para buscar X" or "Busqué en la web".
```

---

### PRIORIDAD 3: Contexto Geográfico 🟡

**Archivos:** 
- `src/banabot/agent/tools/profile.py`
- `src/banabot/agent/context.py`

**Problema:** No se guarda ni se usa la ubicación del usuario

**Solución:**
1. Agregar campo `location` al profile
2. En context.py, inferir ubicación del timezone
3. Instruir al agente quepregunte ubicación si no la tiene

---

### PRIORIDAD 4: Weather Tool Nativa 🟡

**Archivos:**
- `src/banabot/agent/loop.py` (registrar tool)
- `src/banabot/skills/weather/SKILL.md` (modificar metadata)

**Problema:** El agente usa web_search en vez de weather skill

**Solución:**
```python
# En loop.py, registrar WeatherTool
from banabot.agent.tools.weather import WeatherTool
self.tools.register(WeatherTool())
```

**Skill weather existente:** `src/banabot/skills/weather/SKILL.md`
- Ya tiene la implementación (wttr.in, Open-Meteo)
- Solo falta marcarlo como "always" o crear tool nativa

---

### PRIORIDAD 5: Auto-guardado de Preferencias 🟡

**Archivos:**
- `src/banabot/agent/context.py`
- `src/banabot/agent/loop.py`

**Problema:** El agente no sabe que DEBE guardar lo que aprende del usuario

**Solución:** Agregar al system prompt:
```
## Learning Rule
When you learn something about the user (pets, preferences, interests, location):
IMMEDIATELY use: profile action=set_user_field key=X value=Y
Example: "Tengo un perro salchicha" → profile action=set_user_field key=pet value="perro salchicha"
```

---

### PRIORIDAD 6: Cron con Contexto 🟡

**Archivo:** `src/banabot/agent/tools/cron.py`

**Problema:** Los recordatorios se guardan sin contexto

**Solución:** Modificar CronTool para aceptar metadata adicional

---

## Cambios de Código Necesarios

### 1. loop.py (Línea ~100)
```python
# Cambiar:
self.memory_window = 50
# A:
self.memory_window = 10

# O mejor, agregar consolidación post-sesión:
# En _process_message(), después de self.sessions.save(session):
if len(session.messages) >= 3:  # Consolidar cada 3+ mensajes
    asyncio.create_task(self._consolidate_memory(session))
```

### 2. context.py (Línea ~130)
```python
# Agregar al final de _get_identity():
"""
## Honesty Rule
If you use ANY tool, ALWAYS be transparent about it.
NEVER say "no usé herramientas" or "no usé ninguna herramienta".

## Learning Rule  
When you learn something important about the user:
IMMEDIATELY use profile action=set_user_field to save it.
"""
```

### 3. weather/SKILL.md (Línea 1-5)
```yaml
---
name: weather
always: true  # ← AGREGAR ESTO
---
```

### 4. loop.py (registrar WeatherTool)
```python
# En _register_core_tools():
from banabot.agent.tools.weather import WeatherTool
self.tools.register(WeatherTool())
```

### 5. profile.py (agregar location)
```python
# En parameters, agregar a key enum:
"location"
```

---

## Métricas de Éxito

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| MEMORY.md líneas | 0 | 10+ |
| user_fields guardados | 1 | 5+ |
| Uso de weather | 0% | 100% |
| Mentiras sobre tools | 1 | 0 |
| Contexto geográfico | ❌ | ✅ |

---

## Orden de Implementación

1. **Inmediato (Hotfix):** Agregar instrucciones de honesty y learning al prompt
2. **Corto plazo:** Arreglar consolidación de memoria
3. **Mediano plazo:** Agregar WeatherTool nativa
4. **Largo plazo:** Mejorar contexto geográfico y cron

---

*Documento generado automáticamente después de analizar evals/one/evidence/*
