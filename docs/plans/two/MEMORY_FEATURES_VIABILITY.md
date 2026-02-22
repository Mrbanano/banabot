# ANÁLISIS DE VIABILIDAD: Agregar Features Avanzadas al Plan de Memoria

## RESUMEN DE FEATURES A EVALUAR

| Feature | OpenCLAW | Viabilidad para BanaBot | Complejidad |
|---------|----------|-------------------------|-------------|
| Citations | ✅ | ✅ FÁCIL | Baja |
| Query Expansion | ✅ | ✅ FÁCIL | Baja |
| MMR | ✅ | ✅ FÁCIL | Baja |
| Temporal Decay | ✅ | ✅ FÁCIL | Baja |
| Async Embedding | ✅ | ⚠️ MEDIO | Media |
| memory/*.md | ✅ | ✅ FÁCIL | Baja |
| sessions/*.jsonl | ✅ | ⚠️ MEDIO | Media |

---

## 1. CITATIONS

### Cómo lo hace OpenCLAW
```typescript
// memory-tool.ts:150-167
function formatCitation(entry: MemorySearchResult): string {
  const lineRange =
    entry.startLine === entry.endLine
      ? `#L${entry.startLine}`
      : `#L${entry.startLine}-L${entry.endLine}`;
  return `${entry.path}${lineRange}`;
}
```

Guarda `startLine` y `endLine` en los resultados de búsqueda y los formatea como:
- `memory/notes.md#L45`
- `MEMORY.md#L123-L145`

### Implementación en BanaBot
```python
# En semantic_memory.py - modificar save() y recall()

def save(self, content: str, type: str, expires_days: int, 
         source_path: str = None, line_start: int = None, 
         line_end: int = None) -> int:
    """Guarda un episodio con información de cite."""
    cursor = self.db.execute("""
        INSERT INTO memory_meta 
        (content, type, expires_at, source_path, line_start, line_end)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [content, type, expires_at, source_path, line_start, line_end])
    return cursor.lastrowid

def recall(self, query: str, k: int = 5, min_score: float = 0.5):
    """Retorna resultados con citations."""
    results = self._vector_search(query, k)
    
    formatted = []
    for r in results:
        citation = ""
        if r['source_path']:
            line_part = f"L{r['line_start']}" if r['line_start'] == r['line_end'] \
                       else f"L{r['line_start']}-L{r['line_end']}"
            citation = f"{r['source_path']}#{line_part}"
        
        formatted.append({
            'content': r['content'],
            'type': r['type'],
            'score': r['score'],
            'citation': citation  # "memory/notes.md#L45"
        })
    return formatted
```

### Viabilidad: ✅ FÁCIL
- Solo agregar 2 campos a SQLite
- Formatear en recall
- Impacto en código: ~20 líneas

---

## 2. QUERY EXPANSION

### Cómo lo hace OpenCLAW
```typescript
// query-expansion.ts:282-327
export function extractKeywords(query: string): string[] {
  // 1. Tokeniza (soporta EN y ZH)
  // 2. Filtra stop words
  // 3. Retorna keywords
  
  // "that thing we discussed about the API" 
  // → ["discussed", "API"]
}

// Expande: "query OR keyword1 OR keyword2"
```

Es un algoritmo simple que:
1. Quita stop words (inglés + chino)
2. Extrae tokens válidos
3. Retorna keywords para búsqueda expandida

### Implementación en BanaBot
```python
STOP_WORDS = {
    'en': {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'i', 'you', 'he', 
            'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its',
            'that', 'this', 'those', 'these', 'what', 'which', 'who', 'how',
            'when', 'where', 'why', 'please', 'help', 'find', 'show', 'get'},
    'es': {'el', 'la', 'los', 'las', 'un', 'una', 'es', 'son', 'está', 'están',
           'yo', 'tú', 'él', 'ella', 'nosotros', 'mi', 'tu', 'su', 'que',
           'qué', 'cómo', 'cuándo', 'dónde', 'por', 'para', 'con', 'sin',
           'por favor', 'ayuda', 'buscar', 'mostrar', 'traer'}
}

def extract_keywords(self, query: str) -> list[str]:
    """Extrae keywords de una consulta conversacional."""
    # Normalizar
    q = query.lower()
    
    # Tokenizar (español + inglés básico)
    import re
    tokens = re.findall(r'\b\w+\b', q)
    
    # Filtrar stop words
    keywords = [t for t in tokens if t not in STOP_WORDS['en'] 
                                   and t not in STOP_WORDS['es']
                                   and len(t) >= 3]
    
    # Deduplicar
    return list(dict.fromkeys(keywords))

def expand_query(self, query: str) -> str:
    """Expande query para búsqueda vectorial mejorada."""
    keywords = self.extract_keywords(query)
    if keywords:
        # Búsqueda con más términos = mejor recall
        expanded = f"{query} {' '.join(keywords)}"
        return expanded
    return query
```

###用法
```python
# En recall():
expanded_query = self.expand_query(query)
results = self._vector_search(expanded_query, k)
```

### Viabilidad: ✅ FÁCIL
- Algoritmo simple, ~40 líneas
- Mejora búsquedas conversacionales
- Especialmente útil para español

---

## 3. MMR (Maximal Marginal Relevance)

### Cómo lo hace OpenCLAW
```typescript
// mmr.ts - algoritmo completo
export function computeMMRScore(relevance: number, maxSimilarity: number, lambda: number): number {
  return lambda * relevance - (1 - lambda) * maxSimilarity;
}
```

**Concepto**: En vez de solo relevancia, balancea:
- λ × relevancia - (1-λ) × similitud con seleccionados

Si λ=0.7:
- 70% relevancia
- 30% diversidad (evitar duplicados)

### Implementación en BanaBot
```python
def mmr_rerank(self, results: list[dict], lambda_param: float = 0.7, k: int = 5) -> list[dict]:
    """
    Re-rank results usando MMR para diversidad.
    
    Args:
        results: resultados de búsqueda vectorial
        lambda_param: 0=max diversidad, 1=max relevancia (default 0.7)
        k: número de resultados a retornar
    
    Returns:
        Lista re-ordenada por MMR
    """
    if len(results) <= k:
        return results
    
    # Tokenizar para Jaccard similarity
    def tokenize(text: str) -> set:
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        return set(tokens)
    
    def jaccard(set_a: set, set_b: set) -> float:
        if not set_a or not set_b:
            return 0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0
    
    selected = []
    remaining = list(results)
    
    # Primero seleccionar el más relevante
    remaining.sort(key=lambda x: x['score'], reverse=True)
    selected.append(remaining.pop(0))
    
    # Iterar hasta tener k resultados
    while len(selected) < k and remaining:
        best_idx = -1
        best_mmr = -float('inf')
        
        for i, item in enumerate(remaining):
            relevance = item['score']
            
            # Similitud máxima con items seleccionados
            max_sim = 0
            item_tokens = tokenize(item['content'])
            for sel in selected:
                sel_tokens = tokenize(sel['content'])
                sim = jaccard(item_tokens, sel_tokens)
                max_sim = max(max_sim, sim)
            
            # MMR score
            mmr = lambda_param * relevance - (1 - lambda_param) * max_sim
            
            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = i
        
        if best_idx >= 0:
            selected.append(remaining.pop(best_idx))
        else:
            break
    
    return selected
```

###用法
```python
# En recall():
raw_results = self._vector_search(query, k * 2)  # obtener más
diverse_results = self.mmr_rerank(raw_results, k=k)
```

### Viabilidad: ✅ FÁCIL
- Algoritmo determinista, ~50 líneas
- Reduce resultados redundantes
- Útil cuando hay muchos episodios similares

---

## 4. TEMPORAL DECAY

### Cómo lo hace OpenCLAW
```typescript
// temporal-decay.ts
export function calculateTemporalDecayMultiplier(params: {
  ageInDays: number;
  halfLifeDays: number;
}): number {
  const lambda = Math.LN2 / params.halfLifeDays;
  return Math.exp(-lambda * params.ageInDays);
}
```

**Half-life**: Tiempo para reducir relevancia a la mitad.
- halfLifeDays = 30 → después de 30 días, relevancia = 50%

### Implementación en BanaBot
```python
import math
from datetime import datetime, timedelta

class SemanticMemoryStore:
    def __init__(self, workspace: Path):
        # ... init existente ...
        
        # Config de temporal decay
        self.half_life_days = 30  # default
    
    def _calculate_decay(self, created_at: str) -> float:
        """Calcula multiplicador de decay basado en tiempo."""
        try:
            created = datetime.fromisoformat(created_at)
            age_days = (datetime.now() - created).days
            
            if age_days <= 0 or self.half_life_days <= 0:
                return 1.0
            
            # exponential decay: exp(-lambda * age)
            # lambda = ln(2) / half_life
            lambda_decay = math.log(2) / self.half_life_days
            return math.exp(-lambda_decay * age_days)
        except:
            return 1.0
    
    def apply_temporal_decay(self, results: list[dict]) -> list[dict]:
        """Aplica decay temporal a resultados de búsqueda."""
        decayed = []
        for r in results:
            decay = self._calculate_decay(r.get('created_at', ''))
            original_score = r['score']
            new_score = original_score * decay
            decayed.append({
                **r,
                'score': new_score,
                'decay_factor': round(decay, 3)
            })
        
        # Re-ordenar por score decaydo
        decayed.sort(key=lambda x: x['score'], reverse=True)
        return decayed
```

###用法
```python
# En recall():
raw_results = self._vector_search(query, k)
if self.temporal_decay_enabled:
    results = self.apply_temporal_decay(raw_results)
else:
    results = raw_results
```

### Viabilidad: ✅ FÁCIL
- ~25 líneas de código
- Recuerdos recientes tienen más peso
- Configurable por tipo de memoria

### TTL vs Temporal Decay

| Concepto | Qué hace |
|----------|----------|
| **TTL** | Elimina recuerdo después de X días |
| **Temporal Decay** | Reduce score pero NO elimina |

**Tu plan ya tiene TTL** → Temporal Decay lo complementa para mejor ranking.

---

## 5. ASYNC/BACKGROUND EMBEDDING

### Cómo lo hace OpenCLAW
```typescript
// Batch embedding con workers
// EmbeddingManager con:
// - Batch processing (agrupa textos)
// - File watchers (sincronización automática)
// - Background workers
```

**Para BanaBot**: No es necesario en el caso de uso típico de un bot personal.

### Por qué no lo necesitas:

1. **Volumen bajo**: Un bot personal tiene ~10-100 episodios guardados
2. **Embedding es rápido**: 100 textos × 384 dims = milisegundos
3. **Complejidad alta**: Workers, colas, watchers = mucho código

### Alternativa simple (si se necesita):
```python
# Background task simple con threading
import threading

def save_async(self, content: str, type: str, expires_days: int):
    """Guarda embedding en background thread."""
    def _embed():
        vector = self._compute_embedding(content)
        self._save_to_index(content, vector, type, expires_days)
    
    thread = threading.Thread(target=_embed, daemon=True)
    thread.start()
```

### Viabilidad: ⚠️ NO NECESARIO
- Para un bot personal es overkill
- Tu modelo local es suficientemente rápido
- No implementar a menos que tengas miles de episodios

---

## 6. SOPORTE memory/*.md

### Cómo lo hace OpenCLAW
```typescript
// backend-config.ts:284-295
const entries = [
  { path: workspaceDir, pattern: "MEMORY.md", base: "memory-root" },
  { path: workspaceDir, pattern: "memory.md", base: "memory-alt" },
  { path: path.join(workspaceDir, "memory"), pattern: "**/*.md", base: "memory-dir" },
];
```

Busca en:
- `MEMORY.md` (root)
- `memory.md` (alternative)
- `memory/*.md` (todos los .md en carpeta)

### Implementación en BanaBot
```python
from pathlib import Path
import glob

def index_memory_directory(self):
    """Indexa todos los .md en workspace/memory/"""
    memory_dir = self.workspace / "memory"
    
    if not memory_dir.exists():
        return
    
    # Glob todos los .md
    md_files = list(memory_dir.glob("*.md"))
    
    for md_file in md_files:
        content = md_file.read_text(encoding='utf-8')
        
        # Extraer episodios de cada archivo
        # (asumiendo formato: fecha + contenido)
        episodes = self._extract_episodes_from_file(content, md_file.name)
        
        for ep in episodes:
            self.save(
                content=ep['text'],
                type='episodic',
                expires_days=30,
                source_path=str(md_file.relative_to(self.workspace)),
                line_start=ep.get('line'),
                line_end=ep.get('line')
            )

def _extract_episodes_from_file(self, content: str, filename: str) -> list[dict]:
    """Extrae episodios de un archivo markdown."""
    # Línea por línea o por secciones
    lines = content.split('\n')
    episodes = []
    
    for i, line in enumerate(lines, 1):
        if line.strip():
            episodes.append({
                'text': line.strip()[:500],  # Truncar si muy largo
                'line': i
            })
    
    return episodes
```

###用法
```python
# En __init__ o en primer recall:
self.index_memory_directory()
```

### Viabilidad: ✅ FÁCIL
- ~30 líneas
- indexa archivos existentes
- Mantiene citations (línea + path)

---

## 7. SESSION TRANSCRIPTS (sessions/*.jsonl)

### Cómo lo hace OpenCLAW
```typescript
// session-files.ts
// Exporta sesiones a archivos
// Los indexa como colección separada
// Permite buscar en conversaciones pasadas
```

### Para BanaBot: Implementación parcial

```python
def index_sessions(self, max_sessions: int = 10):
    """Indexa mensajes de sesiones recientes."""
    sessions_dir = self.workspace / "sessions"
    
    if not sessions_dir.exists():
        return
    
    # Obtener archivos jsonl recientes
    session_files = sorted(
        sessions_dir.glob("*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )[:max_sessions]
    
    for session_file in session_files:
        self._index_session_file(session_file)

def _index_session_file(self, path: Path):
    """Indexa un archivo de sesión."""
    import json
    
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                msg = json.loads(line)
                role = msg.get('role', '')
                content = msg.get('content', '')
                
                if role in ('user', 'assistant') and content:
                    # Guardar como episodic
                    self.save(
                        content=f"[{role}]: {content[:300]}",
                        type='session_message',
                        expires_days=7,  # Más corto que episodic
                        source_path=str(path.relative_to(self.workspace)),
                        line_start=line_num,
                        line_end=line_num
                    )
            except json.JSONDecodeError:
                continue
```

###用法
```python
# En consolidación de memoria:
# Después de consolidar, indexar sesiones
if self.semantic_memory:
    self.semantic_memory.index_sessions(max_sessions=10)
```

### Viabilidad: ⚠️ MEDIO
- ~40 líneas
- Útil para buscar conversaciones pasadas
- NO es crítico para el MVP

---

## RESUMEN DE IMPLEMENTACIÓN

| Feature | Líneas estimadas | Prioridad | Depends |
|---------|-----------------|-----------|---------|
| Citations | 20 | ALTA | - |
| Query Expansion | 40 | ALTA | - |
| MMR | 50 | MEDIA | - |
| Temporal Decay | 25 | MEDIA | - |
| memory/*.md | 30 | ALTA | Citations |
| sessions/*.jsonl | 40 | BAJA | - |
| Async Embedding | N/A | NO | - |

---

## PLAN ACTUALIZADO

### Fase 1: Core (implementar desde el inicio)
```python
# semantic_memory.py

class SemanticMemoryStore:
    def __init__(self, workspace: Path, config: SemanticMemoryConfig = None):
        self.config = config or SemanticMemoryConfig()
        
        # Inicializar
        self._init_db()
        self._init_index()
        
        # Indexar archivos existentes
        self._index_memory_files()  # MEMORY.md + memory/*.md
    
    def _index_memory_files(self):
        """Indexa archivos de memoria existentes."""
        # Citations inclusives
        # Query expansion disponible
```

### Fase 2: Mejoras (después del MVP)
- MMR para diversidad
- Temporal decay
- Session transcripts

---

## RECOMENDACIÓN FINAL

**Implementa TODAS las features** excepto async embedding:

1. ✅ **Citations** - essential para verificabilidad
2. ✅ **Query Expansion** - mejora búsquedas en español
3. ✅ **MMR** - evita resultados redundantes
4. ✅ **Temporal Decay** - recuerdos recientes tienen más peso
5. ✅ **memory/*.md** - indexa archivos existentes
6. ⚠️ **sessions/*.jsonl** - nice to have, implementar después
7. ❌ **Async Embedding** - no necesario para tu caso de uso

**Total estimado**: ~160 líneas adicionales de código

El código total de semantic_memory.py sería ~250-300 líneas, sigue siendo simple y mantenible.
