# ANÁLISIS: Subagentes en OpenCLAW

## Respuesta Corta

**No usan LangChain ni ningún framework de terceros.** Todo está construido a mano con APIs directas.

---

## Cómo OpenCLAW crea subagentes

### Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                 MAIN AGENT                                  │
│  (sesión principal: agent:main:main)                       │
│                                                             │
│  1. User: "Build me a REST API"                          │
│  2. Agent decide: "This is complex, spawn subagent"        │
│  3. Tool: sessions_spawn()                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ sessions_spawn(task="...", mode="run")
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              SUBAGENT SPAWN                                │
├─────────────────────────────────────────────────────────────┤
│  • Genera session key: agent:main:subagent:UUID          │
│  • Verifica depth limit (max 2-3 niveles)                │
│  • Verifica max children (max 5 por agente)              │
│  • Resuelve modelo (puede usar otro modelo)               │
│  • Configura thinking level                                │
│  • Llama al Gateway: sessions.patch                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              SUBAGENT                                      │
│  (sesión: agent:main:subagent:UUID)                       │
│                                                             │
│  • Prompt MINIMAL (solo tooling + workspace)              │
│  • Ejecuta la tarea asignada                              │
│  • Auto-anuncia cuando termina                            │
│  • Response se envía de vuelta al main                   │
└─────────────────────────────────────────────────────────────┘
```

### Parámetros de Spawn

```typescript
// subagent-spawn.ts:25-36
type SpawnSubagentParams = {
  task: string;                    // La tarea a ejecutar
  label?: string;                  // Etiqueta para identificar
  agentId?: string;                 // ID del agente (default: mismo)
  model?: string;                   // Override de modelo
  thinking?: string;                // Thinking level
  runTimeoutSeconds?: number;       // Timeout
  thread?: boolean;                 // Crear thread?
  mode?: "run" | "session";        // Modo: run o session
  cleanup?: "delete" | "keep";     // Limpiar al terminar
  expectsCompletionMessage?: boolean;
};
```

### Depth Limits

```typescript
// subagent-spawn.ts:219-227
const callerDepth = getSubagentDepthFromSessionStore(requesterInternalKey);
const maxSpawnDepth = cfg.agents?.defaults?.subagents?.maxSpawnDepth ?? 2;

if (callerDepth >= maxSpawnDepth) {
  return { status: "forbidden", error: "depth limit reached" };
}
```

**Previene**: Agentes infinitos generando agentes infinitos.

### Max Children

```typescript
// subagent-spawn.ts:229-236
const maxChildren = cfg.agents?.defaults?.subagents?.maxChildrenPerAgent ?? 5;
const activeChildren = countActiveRunsForSession(requesterInternalKey);

if (activeChildren >= maxChildren) {
  return { status: "forbidden", error: "max children reached" };
}
```

### Modelo por Subagente

```typescript
// subagent-spawn.ts:263-267
const resolvedModel = resolveSubagentSpawnModelSelection({
  cfg,
  agentId: targetAgentId,
  modelOverride,
});
```

Puedes configurar que subagentes usen modelos diferentes:
- Main agent: `claude-opus-4-5`
- Subagent coding: `codex` (más barato)
- Subagent research: `gpt-4o` (mejor web search)

---

## NO USAN LANGCHAIN

### Por qué no necesitan frameworks

```
┌─────────────────────────────────────────────────────────────┐
│  LANGCHAIN (y similares)                                  │
├─────────────────────────────────────────────────────────────┤
│  • Abstracción sobre LLMs                                  │
│  • Chains / Agents / Tools                                │
│  • Memory management                                      │
│  • RAG pipelines                                          │
│  • ~100KB+ de dependencias                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  OPENCLAW (custom)                                         │
├─────────────────────────────────────────────────────────────┤
│  • APIs directas: OpenAI, Anthropic, Google, etc.         │
│  • Propio agent loop                                      │
│  • Propio tool execution                                  │
│  • Propio memory (semantic search)                       │
│  • Propio subagent system                                │
│  • ~0 dependencias extra (solo SDKs de providers)        │
└─────────────────────────────────────────────────────────────┘
```

### Código que usa APIs directas

```typescript
// pi-embedded-runner/run/attempt.ts
// NO usa LangChain - usa fetch() directo

const response = await fetch(`${ANTHROPIC_API_URL}/messages`, {
  method: "POST",
  headers: {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
  },
  body: JSON.stringify({
    model: model,
    messages: messages,
    tools: tools,
    stream: true,
  }),
});
```

### Proveedores soportados

```
• openai (GPT-4, GPT-5, Codex)
• anthropic (Claude)
• google (Gemini)
• voyage (embeddings)
• together (LLMs)
• venice (LLMs)
• Y más...
```

---

## Subagent Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  LIFECYCLE EVENTS (hooks)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. subagent_spawning                                     │
│     → Plugin puede modificar parámetros                    │
│                                                             │
│  2. subagent_delivery_target                              │
│     → Dónde enviar resultados                             │
│                                                             │
│  3. subagent_spawned                                      │
│     → Subagente iniciado                                  │
│                                                             │
│  4. (subagent corre...)                                   │
│                                                             │
│  5. subagent_ended                                        │
│     → Cleanup, notificación                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Registry

```typescript
// subagent-registry.ts
// Mantiene track de todos los subagentes activos

export function registerSubagentRun(params: {
  sessionKey: string;
  parentKey: string;
  model: string;
  task: string;
}): RunId

export function countActiveRunsForSession(parentKey: string): number

export function getSubagentRuns(parentKey: string): SubagentRun[]
```

---

## Comparison: OpenCLAW vs BanaBot

| Aspecto | OpenCLAW | BanaBot (actual) |
|---------|----------|------------------|
| Subagentes | ✅ Completo | ❌ No existe |
| Spawn tool | `sessions_spawn` | N/A |
| Depth limits | ✅ Max 2-3 niveles | N/A |
| Max children | ✅ Max 5 por agente | N/A |
| Modelo por subagente | ✅ Configurable | N/A |
| Lifecycle hooks | ✅ 4 eventos | N/A |
| Auto-announce | ✅ Notifica al terminar | N/A |
| Framework | ❌ Custom (no LangChain) | ❌ Basic loop |

---

## Para BanaBot: Cómo implementar subagentes

### Opción 1: Simple (recomendado)

```python
# Subagente como proceso independiente
# Ejecuta otra instancia del bot con session_id específico

import subprocess

async def spawn_subagent(task: str, parent_session: str) -> str:
    """Spawn un subagente como proceso separado."""
    session_id = f"{parent_session}:subagent:{uuid4()}"
    
    proc = subprocess.Popen([
        "python", "-m", "banabot",
        "--session", session_id,
        "--task", task
    ])
    
    return session_id
```

### Opción 2: Threads (más integrado)

```python
# Subagente en el mismo proceso
import asyncio
from concurrent.futures import ThreadPoolExecutor

class SubagentManager:
    def __init__(self):
        self.active_subagents = {}
    
    async def spawn(self, task: str, parent_session: str) -> str:
        session_id = f"{parent_session}:subagent:{uuid4()}"
        
        # Crear nuevo event loop para el subagente
        loop = asyncio.new_event_loop()
        
        future = loop.run_in_executor(
            None,
            self._run_subagent,
            session_id,
            task
        )
        
        self.active_subagents[session_id] = future
        return session_id
    
    def _run_subagent(self, session_id: str, task: str):
        # Nuevo agent loop con session_id específico
        agent = AgentLoop(session_id=session_id)
        return agent.run(task)
```

### Opción 3: Como herramienta (para el LLM)

```python
# El agente principal puede llamar a spawn_subagent
# como cualquier otra herramienta

TOOLS = [
    {
        "name": "spawn_subagent",
        "description": "Spawn un subagente para tareas complejas",
        "parameters": {
            "task": {"type": "string", "description": "Qué hacer"},
            "model": {"type": "string", "description": "Modelo a usar"}
        }
    }
]

async def execute_spawn_subagent(task: str, model: str = None):
    # Validar depth
    current_depth = get_subagent_depth(session_key)
    if current_depth >= MAX_DEPTH:
        return {"error": "max depth reached"}
    
    # Validar children
    active = count_active_children(parent_session)
    if active >= MAX_CHILDREN:
        return {"error": "max children reached"}
    
    # Spawn
    return await subagent_manager.spawn(task, parent_session)
```

---

## Recomendación para BanaBot

### Nivel 1: Básico (Priority)
```python
# Solo permitir que BanaBot spawnear procesos externos
# No integrar subagentes en el mismo proceso

# Herramienta: spawn_agent
# - task: qué hacer
# - mode: "background" | "foreground"
```

### Nivel 2: Medio
```python
# Subagentes con depth limit y max children
# Comunicación por message passing
```

### Nivel 3: Completo (como OpenCLAW)
```python
# Lifecycle hooks
# Modelo por subagente
# Auto-announce
# Registry
```

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿Usan LangChain? | ❌ NO |
| ¿Qué usan? | APIs directas (fetch) |
| ¿Cómo spawn? | Tool `sessions_spawn` |
| ¿Tienen límites? | ✅ Depth + max children |
| ¿Puedo elegir modelo? | ✅ Por subagente |
| ¿Notifican? | ✅ Auto-announce |

**La diferencia**: OpenCLAW tiene ~1000+ líneas solo en subagent-spawn.ts y subagent-registry.ts. BanaBot no tiene nada implementado.
