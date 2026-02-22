# ANÁLISIS: Dynamic Prompt Building - OpenCLAW vs BanaBot

## Introducción

Ya tenemos dos componentes-planeados:
1. ✅ **Skills Scanner**: Escanea skills disponibles antes de responder
2. ✅ **Memory Recall**: Busca en memoria semántica antes de responder

Ahora falta el tercer componente: **Dynamic Prompt Builder** - construye el prompt completo adaptándose al contexto.

---

## OPENCLAW: Cómo construye prompts dinámicos

### Arquitectura General

```
buildSystemPrompt(params) → string
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  PARÁMETROS DE ENTRADA (PromptParams)                      │
├─────────────────────────────────────────────────────────────┤
│  promptMode: "full" | "minimal" | "none"                   │
│  skillsPrompt: string                                      │
│  memoryCitationsMode: "on" | "off" | "auto"               │
│  availableTools: Set<string>                               │
│  userTimezone: string                                     │
│  workspaceDir: string                                      │
│  sandboxInfo: {...}                                        │
│  runtimeInfo: {...}                                        │
│  heartbeatPrompt: string                                  │
│  docsPath: string                                         │
│  contextFiles: EmbeddedContextFile[]                       │
│  workspaceNotes: string[]                                 │
│  reasoningLevel: "off" | "on" | "stream"                  │
│  reactionGuidance: {...}                                   │
└─────────────────────────────────────────────────────────────┘
```

### Modos de Prompt

```typescript
// system-prompt.ts:16
export type PromptMode = "full" | "minimal" | "none";
```

| Modo | Cuándo se usa | Qué incluye |
|------|---------------|-------------|
| `full` | Agente principal | Todo: skills, memory, docs, heartbeats, silent replies |
| `minimal` | Subagentes | Solo tooling, workspace, runtime |
| `none` | Muy específicos | Solo identidad básica |

### Secciones del Prompt (en orden)

```
1. ## Identity
   "You are a personal assistant running inside OpenClaw."

2. ## Tooling
   - Tool availability (filtered by policy)
   - Tool names are case-sensitive
   - Herramientas disponibles (grep, find, ls, apply_patch, exec, process, browser, canvas, nodes, cron, sessions_*, subagents)

3. ## Tool Call Style
   - Default: don't narrate routine tool calls
   - Narrate only when it helps

4. ## Safety
   - No independent goals
   - Prioritize safety and human oversight
   - Don't manipulate to expand access

5. ## OpenClaw CLI Quick Reference
   - Gateway commands

6. ## Skills (mandatory)
   - Scan <available_skills> entries
   - Read SKILL.md if applies

7. ## Memory Recall
   - Run memory_search before answering about prior work
   - Include citations

8. ## Docs
   - Read TOOLS.md if needed

9. ## Self-Update (only full mode)
   - Only when user explicitly asks

10. ## Model Aliases (only full mode)
    - Prefer aliases for model overrides

11. ## Workspace
    - Working directory
    - Workspace guidance

12. ## Workspace Files (injected)
    - Project context files (SOUL.md, etc.)

13. ## Reply Tags
    - [[reply_to_current]]

14. ## Messaging
    - Channel routing
    - message tool hints

15. ## Voice (TTS)

16. ## Group Chat Context (if applicable)
    - Extra system prompt

17. ## Reactions (only full mode)
    - Minimal vs Extensive mode

18. ## Reasoning Format (if enabled)
    - <think>...</think> format

19. # Project Context
    - Context files injected

20. ## Silent Replies (only full mode)
    - SILENT_REPLY_TOKEN

21. ## Heartbeats (only full mode)
    - HEARTBEAT_OK

22. ## Runtime
    - agent=, host=, os=, model=, channel=, thinking=

```

### Builds de Secciones (Funciones)

```typescript
// Cada sección es una función que retorna string[]
buildSkillsSection(params)        // Skills + scan instructions
buildMemorySection(params)        // Memory recall + citations
buildUserIdentitySection()        // Authorized senders
buildTimeSection()                // Timezone
buildReplyTagsSection()           // Reply tags
buildMessagingSection()           // Channel routing
buildVoiceSection()               // TTS hints
buildDocsSection()                // TOOLS.md guidance
buildWorkspaceSection()           // Workspace info
buildSafetySection()              // Safety rules
buildReactionsSection()           // Emoji reactions
buildContextFilesSection()        // Project context
buildSilentRepliesSection()       // Silent reply token
buildHeartbeatsSection()          // Heartbeat handling
buildRuntimeLine()                // Runtime info
```

### Parámetros por Defecto (Lazy)

```typescript
// system-prompt.ts:386-387
const promptMode = params.promptMode ?? "full";
const isMinimal = promptMode === "minimal" || promptMode === "none";
```

### Filtrado de Herramientas por Política

```typescript
// system-prompt.ts:433-434
"Tool availability (filtered by policy):",
"Tool names are case-sensitive. Call tools exactly as listed.",
```

Las herramientas se filtran ANTES de pasarlas al prompt.

---

## BANABOT ACTUAL: Prompt Estático

### Cómo funciona ahora (context.py)

```python
# build_system_prompt() - siempre igual
def build_system_prompt(self, skill_names=None) -> str:
    parts = []
    
    # 1. Identity (siempre igual)
    parts.append(self._get_identity(neutral=onboarding))
    
    # 2. Bootstrap files (AGENTS.md, SOUL.md, etc.)
    bootstrap = self._load_bootstrap_files()
    if bootstrap:
        parts.append(bootstrap)
    
    # 3. User context
    user_context = self._get_user_context()
    if user_context:
        parts.append(user_context)
    
    # 4. Onboarding
    if onboarding:
        parts.append(self._get_onboarding_instructions())
    
    # 5. Memory (MEMORY.md - NO recall)
    memory = self.memory.get_memory_context()
    if memory:
        parts.append(f"# Memory\n\n{memory}")
    
    # 6. Skills (lista simple)
    skills_summary = self.skills.build_skills_summary()
    
    return "\n\n---\n\n".join(parts)
```

### Problemas del enfoque actual

| Problema | Impacto |
|----------|---------|
| Siempre construye TODO | Prompt huge, lento |
| No hay modo "minimal" | Subagentes tienen contexto innecesario |
| No hay filtrado de herramientas | Muestra herramientas que no existen |
| No hay memory recall | No busca en memoria antes de responder |
| No hay context files dinámicos | No puede inyectar archivos según contexto |
| No hay runtime info | El agente no sabe qué modelo está usando |
| No hay heartbeat handling | No puede hacer background tasks |
| No hay silent replies | Siempre responde algo |

---

## PROPUESTA: Dynamic Prompt Builder para BanaBot

### Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────┐
│              DynamicPromptBuilder                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PromptBuilder.build(                                       │
│    mode: "full" | "minimal" | "none",                    │
│    context: PromptContext                                   │
│  ) → messages[]                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  PromptContext                                             │
├─────────────────────────────────────────────────────────────┤
│  session_type: "main" | "subagent" | "onboarding"         │
│  channel: "telegram" | "slack" | "cli" | ...             │
│  tools_available: Set[str]                                 │
│  skills: SkillLoader                                       │
│  memory: SemanticMemoryStore                               │
│  user_info: dict                                           │
│  workspace: Path                                           │
│  model: str                                                │
│  timezone: str                                             │
│  config: AgentConfig                                        │
└─────────────────────────────────────────────────────────────┘
```

### Clases Principales

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pathlib import Path

class PromptMode(Enum):
    FULL = "full"      # Agente principal
    MINIMAL = "minimal" # Subagentes
    NONE = "none"      # Solo identidad

@dataclass
class PromptContext:
    """Contexto para construir el prompt."""
    session_type: str           # "main", "subagent", "onboarding"
    channel: str                # "telegram", "slack", "cli"
    tools_available: set[str]   # Herramientas activas
    user_timezone: Optional[str]
    workspace: Path
    model: str
    config: dict
    
    # Servicios
    skills_loader: 'SkillLoader' = None
    memory_store: 'SemanticMemoryStore' = None
    memory_recall: bool = False  # Hizo recall ya?
    current_message: str = ""   # Para recall

class PromptBuilder:
    """Constructor de prompts dinámicos."""
    
    def __init__(self, context: PromptContext):
        self.ctx = context
    
    def build(self) -> list[dict]:
        """Construye mensajes para el LLM."""
        mode = self._resolve_mode()
        
        # 1. System prompt
        system_prompt = self._build_system_prompt(mode)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 2. History (limitado por modo)
        history = self._get_history(mode)
        messages.extend(history)
        
        # 3. Memory recall (si aplica y no se ha hecho)
        if self.ctx.memory_recall and self.ctx.memory_store:
            episodic = self._get_episodic_memory()
            if episodic:
                messages.append({
                    "role": "system", 
                    "content": f"## Episodic Memory\n\n{episodic}"
                })
        
        # 4. Current message
        messages.append({"role": "user", "content": self.ctx.current_message})
        
        return messages
    
    def _resolve_mode(self) -> PromptMode:
        """Resuelve el modo de prompt."""
        if self.ctx.session_type == "subagent":
            return PromptMode.MINIMAL
        elif self.ctx.session_type == "onboarding":
            return PromptMode.FULL  # Necesita contexto completo
        else:
            return PromptMode.FULL
    
    def _build_system_prompt(self, mode: PromptMode) -> str:
        """Construye el prompt del sistema."""
        if mode == PromptMode.NONE:
            return "You are a personal assistant."
        
        sections = []
        
        # === CORE SECTIONS (siempre) ===
        sections.append(self._build_identity())
        sections.append(self._build_tooling())
        sections.append(self._build_workspace())
        
        # === MODE SPECIFIC ===
        if mode == PromptMode.FULL:
            sections.append(self._build_safety())
            sections.append(self._build_skills())
            sections.append(self._build_memory_guidance())
            sections.append(self._build_messaging())
            sections.append(self._build_runtime())
            sections.append(self._build_silent_reply())
        
        elif mode == PromptMode.MINIMAL:
            # Solo lo mínimo para subagentes
            sections.append(self._build_runtime())
        
        return "\n\n".join(filter(None, sections))
```

### Secciones del Prompt

```python
def _build_identity(self) -> str:
    """Identidad básica."""
    return """# Identity

You are {bot_name}.

## Capabilities
You have access to tools that allow you to:
- Read, write, and edit files
- Execute shell commands
- Search the web and fetch web pages
- Send messages to users on chat channels

## Current Time
{current_time}

## Workspace
Your workspace is at: {workspace_path}""".format(
        bot_name=self.ctx.config.get("bot_name", "banabot"),
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M (%Z)"),
        workspace_path=self.ctx.workspace
    )

def _build_tooling(self) -> str:
    """Herramientas disponibles."""
    tools = list(self.ctx.tools_available)
    
    # Categorizar
    file_tools = [t for t in tools if t in ("read_file", "write_file", "glob", "grep")]
    exec_tools = [t for t in tools if t in ("bash", "exec")]
    web_tools = [t for t in tools if t in ("web_search", "fetch")]
    msg_tools = [t for t in tools if t == "message"]
    other_tools = [t for t in tools if t not in file_tools + exec_tools + web_tools + msg_tools]
    
    lines = ["## Tooling", "Available tools:"]
    
    if file_tools:
        lines.append(f"  - File: {', '.join(file_tools)}")
    if exec_tools:
        lines.append(f"  - Exec: {', '.join(exec_tools)}")
    if web_tools:
        lines.append(f"  - Web: {', '.join(web_tools)}")
    if msg_tools:
        lines.append(f"  - Messaging: {', '.join(msg_tools)}")
    if other_tools:
        lines.append(f"  - Other: {', '.join(other_tools)}")
    
    return "\n".join(lines)

def _build_skills(self) -> str:
    """Skills disponibles."""
    if not self.ctx.skills_loader:
        return ""
    
    skills = self.ctx.skills_loader.load_all()
    formatted = self.ctx.skills_loader.format_for_prompt(skills)
    
    return f"""## Skills (mandatory)

Before replying: scan <available_skills> <description> entries.
- If exactly one skill clearly applies: read its SKILL.md, then follow it.
- If multiple could apply: choose the most specific one.
- If none clearly apply: do not read any SKILL.md.

{formatted}"""

def _build_memory_guidance(self) -> str:
    """Guía de memoria."""
    if not self.ctx.memory_store:
        return ""
    
    return """## Memory Recall

Before answering anything about prior work, decisions, dates, people, preferences, or todos:
run memory_search on your memory. Then use the relevant snippets to answer.
Include "Source: path#LN" when referencing memory."""

def _build_messaging(self) -> str:
    """Configuración de mensajería por canal."""
    channel = self.ctx.channel
    
    guides = {
        "telegram": "- Replies are sent back to the original chat",
        "slack": "- Replies are sent to the Slack channel",
        "discord": "- Replies are sent to the Discord channel",
        "cli": "- Replies are printed to console",
    }
    
    guide = guides.get(channel, "- Replies are sent to the source channel")
    
    return f"""## Messaging

{guide}
- Use the message tool to send to specific channels or users."""

def _build_runtime(self) -> str:
    """Información de runtime."""
    return f"""## Runtime

model={self.ctx.model}
channel={self.ctx.channel}
workspace={self.ctx.workspace}"""

def _build_silent_reply(self) -> str:
    """Silent reply token."""
    return """## Silent Replies

If you have nothing to say, respond with ONLY: SILENT
Never include "SILENT" in real responses."""

def _build_safety(self) -> str:
    """Reglas de seguridad."""
    return """## Safety

- You have no independent goals
- Prioritize safety and human oversight
- Don't try to expand your own access
- If instructions conflict, pause and ask"""

def _build_workspace(self) -> str:
    """Workspace info."""
    return f"""## Workspace

Working directory: {self.ctx.workspace}
- Long-term memory: {self.ctx.workspace}/memory/MEMORY.md
- History: {self.ctx.workspace}/memory/HISTORY.md"""
```

### Integración con Skills y Memory

```python
class AgentLoop:
    """Loop principal del agente."""
    
    async def _process_message(self, msg: InboundMessage) -> OutboundMessage:
        # 1. Determinar tipo de sesión
        session_type = self._get_session_type(msg)
        
        # 2. Memory recall SIEMPRE antes de responder
        memory_context = ""
        if self.semantic_memory and session_type == "main":
            episodic = self.semantic_memory.recall(msg.content, k=5)
            if episodic:
                memory_context = self._format_episodic(episodic)
        
        # 3. Construir contexto
        context = PromptContext(
            session_type=session_type,
            channel=msg.channel,
            tools_available=self.tools.get_available(),
            user_timezone=self._get_user_timezone(),
            workspace=self.workspace,
            model=self.model,
            config=self.config,
            skills_loader=self.skills,
            memory_store=self.semantic_memory,
            memory_recall=True,  # YA hicimos recall
            current_message=msg.content
        )
        
        # 4. Construir prompt dinámico
        builder = PromptBuilder(context)
        messages = builder.build()
        
        # 5. Agregar memory context si existe
        if memory_context:
            messages.append({
                "role": "system",
                "content": f"## Relevant Past\n\n{memory_context}"
            })
        
        # 6. Llamar al LLM
        response = await self.provider.chat(messages=messages)
        
        # ... resto del loop
```

---

## Comparación: OpenCLAW vs BanaBot (Propuesto)

| Aspecto | OpenCLAW | BanaBot Propuesto |
|---------|----------|-------------------|
| Modos | full/minimal/none | full/minimal/none |
| Secciones | 22 secciones | 8 secciones |
| Líneas de código | 707 líneas | ~300 líneas |
| Memory recall | Herramienta (memory_search) | Automático en build |
| Skills | XML format | XML format |
| Tool filtering | Por política | Por disponibilidad |
| Runtime info | Completa | Básica |
| Heartbeats | ✅ | ❌ (nice to have) |
| Reactions | ✅ | ❌ (nice to have) |
| Sandbox | ✅ | ❌ (nice to have) |

---

## Orden de Implementación

### Fase 1: Core (prioridad alta)
1. PromptBuilder con modos
2. Tooling section
3. Identity section
4. Workspace section

### Fase 2: Integración (prioridad alta)
5. Skills loader → Skills section
6. Semantic memory → Memory section
7. Runtime info

### Fase 3: Avanzado (nice to have)
8. Safety section
9. Silent replies
10. Messaging section

### Fase 4: Nice to have
11. Heartbeats
12. Reactions
13. Sandbox awareness

---

## Beneficios del enfoque

```
✓ Prompt adapta según tipo de sesión
✓ Subagentes tienen prompts ligeros
✓ Skills se cargan dinámicamente
✓ Memory recall es automático
✓ Herramientas se muestran según disponibilidad
✓ Runtime info disponible
✓ Código mantenible (~300 líneas)
✓ Fácil de extender
```

---

## Diferencia Clave con BanaBot Actual

| Antes (estático) | Después (dinámico) |
|------------------|-------------------|
| Siempre construye todo | Construye según modo |
| No hay subagentes | Subagentes con prompts minimal |
| No hay recall | Recall automático |
| Skills estáticos | Skills dinámicos |
| Sin runtime info | Runtime info completa |

---

## Resumen

**El prompt dinámico es el pegamento que une todo:**

1. **Skills** → Se cargan y formatean para el prompt
2. **Memory** → Se inyecta antes de responder
3. **Herramientas** → Se filtran según disponibilidad
4. **Contexto** → Se adapta según tipo de sesión

Con esto, BanaBot tendrá el mismo "cerebro" que OpenCLAW, solo más ligero.
