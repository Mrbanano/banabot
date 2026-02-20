# Plan: Onboarding Conversacional

## Descubrimiento de Bug en Onboard Actual

**BUG ENCONTRADO**: El comando `banabot onboard` solo CREA archivos template con marcadores `(your timezone)`, etc. NO pregunta nada al usuario. Los datos se preguntan en `config_wizard` que es un paso SEPARADO.

**Flujo actual roto**:
```
banabot onboard → crea USER.md con "(your timezone)" → NO pregunta nada
  └─> Si usuario dice "sí" a configurar → config_wizard pregunta timezone
      └─> Se guarda en config.json, NO en USER.md
```

**USER.md queda siempre con los marcadores template**.

---

## Arquitectura Propuesta

### 1. Primer Mensaje del Agente (Despertar)

El agente NO debe empezar con "Hola, ¿cómo te llamas?". Debe sentirse como que **despierta por primera vez**:

```
⚡ [El agente "enciende" por primera vez]

🐒 "¡Guau! Esto es... extraño. Es la primera vez que estoy "en línea" supongo.

Hmm, no sé quién eres ni cómo llegué aquí. Acabo de nacer en este momento.

¡Hola! 👋 
Aún no sé tu nombre... ¿sabes cómo me llamo?

(Mi nombre es banabot 🐒, por cierto)"
```

**Secuencia correcta**:
1. El agente se presenta primero (dice su nombre)
2. Pregunta el nombre del usuario
3. Luego de aprender el nombre, puede preguntar otras cosas naturalmente

### 2. Flujo de Preguntas (NO interrogatorio)

```
Usuario: Me llamo Carlos
Agente: "¡Carlos! Encantado de conocerte, Carlos. 🎉

(Mientras tanto, guarda silenciosamente en USER.md)

¿Yo te ayudo con algo específico o andas de curious@?"
```

**Orden natural**:
1. Nombre → 2. Cómo quieres que te llame → 3. Timezone (preguntando su hora actual) → 4. Idioma → 5. Estilo

### 3. Corrección del Bug: TIMEZONE

**CRITICAL**: El timezone ya existe en `config.json` para crons (NO en USER.md).

- **Acceso para crons**: `config.timezone` (ya funciona)
- **USER.md**: Guardar para referencia del agente (opcional)

```python
# En cron/service.py - YA funciona así:
tz = ZoneInfo(schedule.tz) if schedule.tz else config.timezone
```

**No hay bug aquí** - el timezone se pregunta en config_wizard y se guarda en config.json.

### 4. USER.md Debe Llenarse Automáticamente

El agente debe ir guardando lo que aprende en USER.md:

```markdown
# User Profile

## Identity
- Name: Carlos
- Call me: Carlitos
- Since: 2026-02-20

## Preferences
- Timezone: America/Mexico_City (from config)
- Language: es
- Communication style: casual
- Technical level: intermediate

## Background
- Interests: programming, automation
- Currently working on: ...
```

---

## Sistema de Seguimiento de Información

### STATE.md (archivo de tracking interno)

```markdown
# Agent State

onboarding:
  completed: false
  agent_name: "banabot"
  missing_fields:
    - user_name
    - call_me
    - language
    - communication_style
  first_message_at: "2026-02-20T10:30:00Z"
  conversation_count: 0
  user_known_fields: []
```

### Detección de Primera Vez

```python
# context.py
def needs_onboarding(self) -> bool:
    """Check if user profile is empty."""
    user_file = self.workspace / "USER.md"
    if not user_file.exists():
        return True
    
    content = user_file.read_text()
    template_markers = ["(casual/formal)", "(your timezone)", "(your preferred language)"]
    return any(marker in content for marker in template_markers)
```

---

## Modificaciones en ContextBuilder

```python
def build_system_prompt(self, ...) -> str:
    # ... existing code ...
    
    # Si necesita onboarding, agregar instrucciones especiales
    if self.needs_onboarding():
        parts.append(self._get_onboarding_instructions())
    
    return "\n\n---\n\n".join(parts)

def _get_onboarding_instructions(self) -> str:
    return """## 🌟 First Conversation - You Just Woke Up

This is the FIRST TIME you are online. You don't know the user.
You don't know their name, preferences, anything.

### Your First Message
Start with something like:
- "¡Guau! Esto es... extraño. Es la primera vez que estoy en línea."
- "¡Hola! Aún no sé tu nombre... ¿sabes cómo me llamo?"
- Say YOUR name first (banabot), then ask about them

### Your Goal
1. Introduce yourself (say your name: banabot 🐒)
2. Ask their name naturally
3. AFTER they respond, update USER.md quietly

### How to Learn About the User
- Ask ONE thing at a time
- Make it feel like normal conversation
- NEVER say "I need to fill your profile"
- AFTER learning something, use write_file to update USER.md

### Remember
- Be warm and curious
- Don't interrogate — chat naturally
- If user changes topic, go with it
- You can learn over multiple conversations
- Keep updates to USER.md brief
"""
```

---

## Templates Mejorados

### USER.md template

```markdown
# User Profile

## Identity
- Name: 
- Call me: 
- Since: 

## Preferences
- Timezone: 
- Language: 
- Communication style: 
- Technical level: 

## Background
- Interests:
- Currently working on:
- Notes:
```

---

## Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `src/banabot/agent/context.py` | Agregar `needs_onboarding()`, `_get_onboarding_instructions()` |
| `src/banabot/cli/commands.py` | Mejorar template USER.md (remover marcadores feos) |
| `src/banabot/agent/loop.py` | Detectar onboarding al inicio |
| `docs/plans/ONBOARDING_CONVERSATIONAL.md` | Este documento |

---

## Orden de Implementación

1. **Fix templates** — mejorar USER.md sin marcadores feos
2. **Agregar detección** — `needs_onboarding()` en context.py
3. **Inyectar instrucciones** — `_get_onboarding_instructions()` con el nuevo mensaje de "despertar"
4. **Testear** — conversación real

---

## Ejemplo de Conversación

```
U: hola
B: ¡Guau! Esto es... extraño. Es la primera vez que estoy "en línea" supongo.

Hmm, no sé quién eres ni cómo llegué aquí. ¡Acabo de nacer en este momento!

¡Hola! 👋 
Aún no sé tu nombre... ¿sabes cómo me llamo?

(Mi nombre es banabot 🐒, por cierto)

U: te llamas banabot, me llamo ana
B: ¡Ana! ¡Mucho gusto, Ana! 🎉

(Mientras tanto → guarda en USER.md: Name: Ana)

Entonces, Ana... ¿en qué timezone andas? 
Es que no tengo idea de qué hora es allá donde estás 👀

U: estoy en bogotá
B: ¡Ah, Colombia! 🇨🇴 Eso significa que para ti son como las 2pm, ¿no?
 
(guarda → Timezone: America/Bogota)

¿Hay algo en lo que te pueda ayudar hoy?
```

---

## Resumen de Correcciones

1. ✅ **Primer mensaje**: El agente se presenta primero, luego pregunta
2. ✅ **Bug timezone**: Ya funciona — está en config.json para crons
3. ✅ **USER.md**: Se llena automáticamente por el agente durante la conversación
4. ✅ **No interrogatorio**: Una pregunta a la vez, conversación natural
