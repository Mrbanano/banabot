# Plan: Memoria Semántica — Banabot

> Documento de planificación. No modifiques código hasta leer esto.
> Contexto técnico previo: `docs/MEMORY_SEMANTIC_CONTEXT.md`

---

## Estado de la estructura (investigado 2026-02-20)

### Migración src/ layout — HECHO ✅

`banabot/` movido a `src/banabot/`. Cambios aplicados:
- `pyproject.toml` — `packages = ["src/banabot"]`, rutas `include` y `sdist` actualizadas
- `src/banabot/cli/commands.py:653` — `src_bridge` corregido (un `.parent` extra por el nivel `src/`)
- `.gitignore` — quitado `docs/` (bloqueaba los docs), agregado `workspace/`

---

## Veredicto sobre `workspace/`

**`workspace/` es 100% datos runtime. No pertenece al repo.**

Prueba: los templates de `workspace/AGENTS.md`, `SOUL.md`, `USER.md` se generan
desde strings **hardcodeadas** en `src/banabot/cli/commands.py:_create_workspace_templates()`.
El `workspace/` que está en el repo es el workspace real del desarrollador
que nunca fue gitignoreado — contiene `MEMORY.md` con datos reales.

Lo que SÍ se instala con el paquete (parte del wheel):
```
src/banabot/skills/          ← skills builtin (incluidos en pyproject.toml)
src/banabot/cli/i18n/*.json  ← traducciones CLI
```

Lo que es runtime (NO se instala, NO debe estar en git):
```
workspace/                   ← workspace del bot (MEMORY.md, HISTORY.md, sessions/, skills/)
```

Ya corregido: `.gitignore` ahora incluye `workspace/`.
Para limpiar el histórico de git si hay datos sensibles:
```bash
git rm -r --cached workspace/
git commit -m "chore: remove workspace runtime data from tracking"
```

---

## Diagnóstico: desmadre de carpetas

El repo tenía docs/assets dispersos sin convención. Estado actual post-migración:

```
raíz/
├── src/banabot/          ✅ paquete Python (migrado)
├── bridge/               ✅ bridge TypeScript
├── tests/
├── docs/                 ✅ .gitignore corregido (ya no ignora docs/)
│   ├── MEMORY_SEMANTIC_CONTEXT.md
│   └── SEMANTIC_MEMORY_PLAN.md  (este archivo)
│
├── CHANGELOG.md          ← agrega changelog/
├── COMMUNICATION.md      ← ¿qué es? ¿interna?
├── CREDITS.md
├── DEVELOPMENT.md
├── REBRAND_PLAN.md       ← plan activo o ya ejecutado?
├── SECURITY.md
├── README.md
├── banabot_arch.png      ← imagen suelta en raíz  (pendiente mover)
├── banabot_logo.png      ← imagen suelta en raíz  (pendiente mover)
├── core_agent_lines.sh   ← script suelto en raíz  (pendiente mover/borrar)
├── changelog/            ← bien: un .md por versión
├── case/                 ← GIFs para el README     (pendiente fusionar con img/)
├── img/                  ← más imágenes
├── roadmap/              ← solo 1 archivo (index.md)
├── issues/               ← issues con fecha
└── workspace/            ← YA IGNORADO en .gitignore (pendiente git rm --cached)
```

### Pendientes de orden (no urgentes)

| Pendiente | Acción |
|---|---|
| Imágenes en 3 lugares (`raíz`, `img/`, `case/`) | Consolidar en `img/` e `img/demos/` |
| `roadmap/index.md` solo | Fusionar con `docs/roadmap.md` |
| `REBRAND_PLAN.md` en raíz | Archivar en `docs/archive/` si ya se ejecutó |
| `COMMUNICATION.md`, `CREDITS.md`, `DEVELOPMENT.md` | Mover a `docs/` |
| `core_agent_lines.sh` | Mover a `scripts/` o eliminar |
| `workspace/` aún trackeado | `git rm -r --cached workspace/` |
| `dist/` — ya en `.gitignore` | `git rm -r --cached dist/` si aún aparece |

### Convención final propuesta

```
raíz/
├── README.md
├── CHANGELOG.md          ← mantener (lo espera PyPI/GitHub)
├── SECURITY.md           ← mantener (convención GitHub)
├── LICENSE
├── pyproject.toml
├── Dockerfile / docker-compose.yml
│
├── src/banabot/          ← paquete Python  ✅ hecho
├── bridge/               ← bridge TypeScript
├── tests/
│
├── docs/                 ← TODO el conocimiento interno aquí
│   ├── MEMORY_SEMANTIC_CONTEXT.md   (ya existe)
│   ├── SEMANTIC_MEMORY_PLAN.md      (este archivo)
│   ├── DEVELOPMENT.md               (mover desde raíz)
│   ├── COMMUNICATION.md             (mover desde raíz)
│   ├── CREDITS.md                   (mover desde raíz)
│   ├── roadmap.md                   (fusionar roadmap/index.md aquí)
│   ├── archive/
│   │   └── REBRAND_PLAN.md          (archivar si ya ejecutado)
│   └── issues/                      (mover issues/ aquí)
│       └── 19-02-2026.md
│
├── img/                  ← todas las imágenes y demos
│   ├── banabot-logo.png
│   ├── banabot-min.png
│   └── demos/
│       ├── code.gif
│       ├── memory.gif
│       ├── schedule.gif   ← (typo: scedule → schedule)
│       └── search.gif
│
└── scripts/
    └── core_agent_lines.sh

# .gitignore — agregar:
dist/
workspace/
```

---

## Estado actual de memoria

```
workspace/memory/
├── MEMORY.md     ← hechos long-term (escrito por el LLM)
└── HISTORY.md    ← log grep-searchable (crece sin límite)

workspace/sessions/
└── *.jsonl       ← historial de conversación (crece sin límite)
```

### Cómo funciona hoy

1. Usuario manda mensaje → `_process_message` en `loop.py`
2. Si `len(session.messages) > 50` → `asyncio.create_task(_consolidate_memory(session))`
3. `_consolidate_memory` llama al LLM → produce `history_entry` y `memory_update`
4. Escribe en HISTORY.md y actualiza MEMORY.md
5. **No trunca la sesión** — el JSONL sigue creciendo
6. `get_history(max_messages=50)` solo manda los últimos 50 al LLM, pero el archivo tiene todo

### Problema central: compresión con pérdida

Cuando el LLM consolida 40 mensajes en un párrafo, los detalles
episódicos desaparecen para siempre. No hay forma de saber que
"hace 2 semanas el usuario dijo que su tía se casa".

---

## Stack técnico (ya validado en Pi 3B)

```
fastembed  >= 0.5.0   — embeddings, wheels ARM64 nativos
usearch    >= 2.0.0   — índice vectorial en disco, ARM64 nativo
sqlite3    (stdlib)   — metadata, sin deps extra

modelo: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
dims: 384
RAM modelo: ~670MB
hardware mínimo: Pi 4 con 2GB
```

Ver `docs/MEMORY_SEMANTIC_CONTEXT.md` para el POC completo validado.

---

## Arquitectura resultante

```
workspace/memory/
├── MEMORY.md          ← sin cambios
├── HISTORY.md         ← sin cambios + auto-trim nuevo
├── memory.db          ← NUEVO: SQLite con metadata de episodios
└── memory.usearch     ← NUEVO: índice vectorial en disco
```

### Tipos de memoria y TTL

| tipo | TTL | ejemplo |
|---|---|---|
| `episodic` | 30 días | "fue a Oaxaca la semana pasada" |
| `summary` | 90 días | resumen comprimido de sesión |
| `fact` | 180 días | "banabot corre en Pi 4" |
| `user_profile` | nunca | "prefiere respuestas cortas" |

---

## Plan de implementación

### Paso 1 — `agent/semantic_memory.py` (archivo nuevo)

Clase `SemanticMemoryStore`. Justificación de archivo nuevo: deps distintas
(fastembed/usearch), lifecycle propio, no contamina `MemoryStore`.

**API pública:**

- `__init__(workspace: Path)` — no carga modelo todavía
- `_ensure_ready()` — carga perezosa: fastembed + usearch + sqlite schema
- `is_available` (property) — `False` si fastembed/usearch no instalados
- `save(content, type, expires_days)` — idempotente, embed + SQLite + usearch
- `recall(query, k=5, min_score=0.5)` — búsqueda vectorial, filtra expirados
- `purge_expired()` — elimina de SQLite + reconstruye index desde cero
- `stats()` — conteo por tipo (para `/memory` command)

**Schema SQLite:**

```sql
CREATE TABLE memory_meta (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    content    TEXT    NOT NULL,
    type       TEXT    NOT NULL DEFAULT 'episodic',
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT    -- NULL = nunca expira
);
```

**Nota sobre usearch:** no borra vectores reales, solo los marca.
`purge_expired()` debe reconstruir el índice completo desde los IDs
activos en SQLite. Ver POC en `docs/MEMORY_SEMANTIC_CONTEXT.md`.

---

### Paso 2 — `config/schema.py`

Nueva clase `SemanticMemoryConfig(Base)`:

```
enabled: bool = False            # opt-in, cero impacto si False
min_score: float = 0.5           # threshold para no inyectar ruido
max_recall: int = 5              # k para recall
cleanup_interval_hours: int = 24 # frecuencia de purge_expired
history_max_lines: int = 500     # umbral para auto-trim de HISTORY.md
```

Se agrega como campo a `AgentDefaults` al mismo nivel que `memory_window`.

---

### Paso 3 — `agent/loop.py`: extender consolidación

**Archivo:** `_consolidate_memory()` líneas 407-491

**Cambio:** el prompt ya pide `history_entry` y `memory_update`.
Extender para pedir también `episodes: list[str]` — lista de strings
cortos, cada uno un acontecimiento puntual.

Un solo LLM call, sin costo extra de latencia.

**Flujo nuevo dentro de `_consolidate_memory`:**

```
1. LLM devuelve {history_entry, memory_update, episodes: [...]}
2. Escribir history_entry → HISTORY.md  (igual que antes)
3. Escribir memory_update → MEMORY.md   (igual que antes)
4. Si semantic_memory.is_available:
   a. Cada episodio → save(ep, type="episodic", expires_days=30)
   b. history_entry → save(entry, type="summary", expires_days=90)
5. Auto-trim HISTORY.md si supera history_max_lines
6. Si han pasado cleanup_interval_hours desde último purge:
   → purge_expired() como asyncio.create_task
```

**Dónde guardar el timestamp del último cleanup:**
Archivo `workspace/memory/.last_cleanup` — un timestamp ISO en texto
plano. Simple, sin deps, no contamina el estado de sesión.

---

### Paso 4 — `agent/loop.py`: auto-trim de HISTORY.md

Dentro de `_consolidate_memory`, después de `append_history()`:

```
Si líneas(HISTORY.md) > history_max_lines:
    Tomar las primeras (history_max_lines // 2) líneas
    LLM call ligera: condensar en un párrafo de archivo
    Reemplazar esas líneas con el párrafo
```

Mantiene HISTORY.md acotado sin perder completamente el histórico.

---

### Paso 5 — `session/manager.py`: auto-trim de JSONL

Nuevo método `trim(session, keep_last_n: int)`.

Se llama desde `_consolidate_memory` **únicamente si semantic memory
está activo y el save de episodios fue exitoso** — garantía de que
los datos no se pierden antes de ser preservados en el vector store.

Política: mantener los últimos `memory_window * 2` mensajes.
Los anteriores ya están en HISTORY.md + memory.db.

---

### Paso 6 — `agent/context.py`: inyección de memoria episódica

**`ContextBuilder.__init__`:** recibe
`semantic_memory: SemanticMemoryStore | None = None`.

**`build_messages()`:** ya tiene `current_message`. Agregar recall:

```
Si semantic_memory.is_available:
    relevant = recall(current_message, k=max_recall, min_score=min_score)
    Si hay resultados:
        Construir bloque <episodic_memory> e inyectar en system prompt
```

**Orden del system prompt** (con sección nueva):

```
1. Identidad / runtime                    (actual)
2. Bootstrap files AGENTS/SOUL/USER/TOOLS (actual)
3. ## Long-term Memory (MEMORY.md)        (actual)
4. ## Episodic Memory    ← NUEVO          (solo si recall devuelve algo)
5. Skills                                 (actual)
```

Formato del bloque episódico:

```
## Episodic Memory
Recuerdos relevantes al mensaje actual:
- [episodic] fue a Oaxaca la semana pasada (score: 0.87)
- [summary] discutió opciones de Pi 4 para el bot (score: 0.72)
```

---

### Paso 7 — Wire-up en `AgentLoop.__init__`

```
Si semantic_memory_config.enabled:
    semantic_memory = SemanticMemoryStore(workspace)
    context = ContextBuilder(workspace, semantic_memory=semantic_memory)
Sino:
    context = ContextBuilder(workspace)  # igual que hoy
```

Sin semantic memory, todo funciona idéntico al estado actual.

---

### Paso 8 — `pyproject.toml`: deps opcionales

```toml
[project.optional-dependencies]
semantic = [
    "fastembed>=0.5.0",
    "usearch>=2.0.0",
]
```

Instalación:
```bash
uv add "banabot[semantic]"
# o en desarrollo:
uv add fastembed usearch
```

El modelo (~252MB) se descarga automáticamente en el primer uso.
Se guarda en `~/.cache/fastembed/` — no en el workspace del bot.

Para descargar en el momento de instalación (útil en Pi para
controlar cuándo usar la red) se puede agregar un comando CLI:
`banabot memory download-model`.

---

## Mapa de cambios por archivo

| Archivo | Tipo | Qué cambia |
|---|---|---|
| `agent/semantic_memory.py` | **Nuevo** | Clase SemanticMemoryStore completa |
| `config/schema.py` | **Extender** | SemanticMemoryConfig + campo en AgentDefaults |
| `agent/loop.py` | **Extender** | Prompt consolidación + trim HISTORY.md + trim JSONL + wire-up |
| `agent/context.py` | **Extender** | Recibir SemanticMemoryStore, recall + bloque episódico en prompt |
| `session/manager.py` | **Extender** | Método trim() |
| `pyproject.toml` | **Extender** | Optional extras [semantic] |
| `agent/memory.py` | Sin cambios | Intacto |
| `.gitignore` | **Extender** | Agregar dist/ y workspace/ |

---

## Garantías de no-regresión

- `enabled: false` por defecto → cero impacto si no se activa
- `is_available` → si fastembed/usearch no están instalados, todo sigue igual
- `MemoryStore` y la API pública de `ContextBuilder` no cambian firma
- El trim de JSONL solo ocurre si el save semántico fue exitoso
- Un solo LLM call adicional por consolidación (el de episodios es parte del mismo prompt)

---

## Orden sugerido de implementación

1. `schema.py` — config primero, sin side effects
2. `semantic_memory.py` — módulo aislado, testeable standalone
3. `session/manager.py` — agregar `trim()`, no lo llama nadie todavía
4. `loop.py` — extender prompt + llamar trim + wire-up
5. `context.py` — inyección en prompt
6. `pyproject.toml` — deps opcionales
7. `.gitignore` — limpiar dist/ y workspace/

---

*Creado: 2026-02-20*
