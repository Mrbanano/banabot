# Contexto: Implementación de Memoria Semántica para Banabot
> Este documento es contexto para Claude Code. Lee el proyecto antes de implementar.

---

## Qué se probó y qué funcionó

Se probaron múltiples stacks de memoria semántica para correr en Raspberry Pi.
El ganador tras benchmarks reales en Pi 3B (aarch64, DietPi) fue:

```
fastembed + usearch + sqlite3 (stdlib)
modelo: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

**Por qué este stack:**
- `fastembed` — wheels nativos ARM64, zero compilación manual
- `usearch` — vector index en disco, wheels nativos ARM64
- `sqlite3` — stdlib Python, zero deps extra
- El modelo es multilingüe (ES, EN, FR, DE, PT y más) con 384 dimensiones
- Único modelo que separó claramente señal de ruido en español

**Requisito de hardware mínimo recomendado: Pi 4 con 2GB RAM**
- El modelo ocupa ~670MB RAM al cargar
- Pi 3B (1GB) no tiene margen suficiente con el bot encima

---

## Cómo funciona el POC (ya validado)

```python
from fastembed import TextEmbedding
from usearch.index import Index
import sqlite3, numpy as np

MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DIMS  = 384

# Singleton — cargar modelo una sola vez
model = TextEmbedding(MODEL)

# Index vectorial en disco
index = Index(ndim=DIMS, metric="cos", dtype="f32")
index.load("memory.usearch")  # si existe

# Metadata en sqlite
db = sqlite3.connect("memory.db")
```

### Guardar un recuerdo
```python
def save(content: str, type: str = "episodic", expires_days=30):
    # Idempotente: verificar si ya existe
    existing = db.execute("SELECT id FROM memory_meta WHERE content = ?", [content]).fetchone()
    if existing:
        return existing[0]

    expires = f"datetime('now', '+{expires_days} days')" if expires_days else "NULL"
    cursor = db.execute(
        f"INSERT INTO memory_meta(content, type, expires_at) VALUES (?, ?, {expires})",
        [content, type],
    )
    mid = cursor.lastrowid
    db.commit()

    vec = np.array(list(model.embed([content]))[0], dtype=np.float32)
    index.add(mid, vec)
    return mid
```

### Recuperar recuerdos relevantes
```python
def recall(query: str, k: int = 5) -> list[dict]:
    q_vec   = np.array(list(model.embed([query]))[0], dtype=np.float32)
    matches = index.search(q_vec, k)
    if not len(matches):
        return []

    ids      = [int(m.key) for m in matches]
    dist_map = {int(m.key): round(float(m.distance), 4) for m in matches}
    ph       = ",".join("?" * len(ids))
    rows     = db.execute(
        f"SELECT id, content, type FROM memory_meta WHERE id IN ({ph})", ids
    ).fetchall()
    row_map = {r[0]: r for r in rows}
    return [
        {
            "content": row_map[i][1],
            "type":    row_map[i][2],
            "score":   round(1 - dist_map[i], 3),  # 1=idéntico, 0=nada que ver
        }
        for i in ids if i in row_map
    ]
```

---

## Schema de la DB

```sql
CREATE TABLE memory_meta (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    content    TEXT    NOT NULL,
    type       TEXT    NOT NULL DEFAULT 'episodic',
    -- tipos: 'episodic' | 'fact' | 'user_profile' | 'summary'
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT    -- NULL = nunca expira
);
```

### TTL sugerido por tipo
| tipo | expires_days | ejemplo |
|---|---|---|
| `episodic` | 30 | "fue a Oaxaca la semana pasada" |
| `fact` | 180 | "Banabot corre en Pi 4" |
| `user_profile` | NULL | "prefiere respuestas cortas" |
| `summary` | 90 | resumen comprimido de sesión |

---

## Dónde integrar en Banabot

Lee estos archivos antes de implementar:

- `banabot/agent/memory.py` — sistema actual (.md + grep), aquí va la nueva capa
- `banabot/agent/loop.py` — líneas ~407-491, compresión destructiva de mensajes al superar 50
- `banabot/agent/context.py` — donde se construye el prompt, aquí se inyectan los recuerdos
- `banabot/config/schema.py` — línea ~186, límite de 8192 tokens (puede necesitar ajuste)

---

## Dos puntos críticos de integración

### 1. Reemplazar compresión destructiva (loop.py ~407-491)

Actualmente cuando la sesión supera 50 mensajes, los viejos se comprimen via LLM
y se descartan — pérdida de información permanente.

**Propuesta:** antes de descartar, extraer episodios importantes y guardarlos
con `save()`. El LLM extrae, el vector store preserva. Solo entonces descartar.

```python
# Pseudocódigo — adaptar al estilo del proyecto
if len(messages) > 40:
    to_compress = messages[:-10]
    episodes    = llm_extract_episodes(to_compress)  # lista de strings
    for ep in episodes:
        memory.save(ep, type="episodic")
    messages = messages[-10:]  # solo conservar los recientes
```

### 2. Inyectar memoria en cada turno (context.py)

Antes de construir el prompt del turno actual, hacer recall con el mensaje del usuario
y agregar los recuerdos relevantes al system prompt:

```python
relevant = memory.recall(user_message, k=5)
if relevant:
    memory_block = "\n".join(f"- [{r['type']}] {r['content']}" for r in relevant)
    system_prompt = f"<memory>\n{memory_block}\n</memory>\n\n" + system_prompt
```

---

## Advertencia sobre usearch y borrado

`usearch` no borra vectores de verdad — solo los marca como removidos pero no libera espacio.
Para cleanup de recuerdos expirados, la solución correcta es reconstruir el índice
periódicamente con solo los IDs activos que existan en `memory_meta`.

```python
def rebuild_index():
    rows = db.execute("SELECT id FROM memory_meta").fetchall()
    active_ids = [r[0] for r in rows]
    # re-embedear y reconstruir index desde cero con solo IDs activos
```

---

## Instalación

```toml
# pyproject.toml — agregar a dependencies
fastembed = ">=0.5.0"
usearch    = ">=2.0.0"
```

```bash
uv add fastembed usearch
```

El modelo se descarga automáticamente en el primer uso (~252MB, solo una vez). ve si se puede descarga mientras se instala
Se guarda en el cache de fastembed (`~/.cache/fastembed/`).