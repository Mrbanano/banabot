# COMPARACIÓN: Motor de Skills de OpenCLAW vs BanaBot

## RESUMEN

| Aspecto | OpenCLAW | BanaBot |
|---------|----------|---------|
| **Skills totales** | 55 | 9 (incluyendo README) |
| **Skills reales** | 55 | 8 |
| **Líneas de código del motor** | ~2500 líneas | ~200 líneas |
| **Formateo** | XML `<skill>` | Markdown simple |
| **Carga dinámica** | ✅ Yes | ❌ Estático |
| **Filtros** | ✅ Por workspace, plugin, bundled | ❌ No |
| **Watch** | ✅ File watcher para cambios | ❌ No |

---

## OPENCLAW: Motor de Skills

### Formato de Inyección en Prompt

```xml
<available_skills>
  <skill>
    <name>coding-agent</name>
    <description>Delegate coding tasks to Codex, Claude Code, or Pi agents...</description>
  </skill>
  <skill>
    <name>github</name>
    <description>Interact with GitHub using the gh CLI...</description>
  </skill>
  ...
</available_skills>
```

### Cómo funciona

```
1. CARGA DE SKILLS (skills/workspace.ts)
   ├── bundled-skills/     → skills del core
   ├── managed-skills/    → skills instalados
   ├── workspace/skills/  → skills del usuario
   ├── plugin-skills/     → skills de plugins
   └── extra-dirs/        → directorios extra

2. FILTRADO (buildWorkspaceSkillSnapshot)
   ├── Verificar eligibility (config, environment)
   ├── Aplicar skill filters (si existen)
   ├── Limitar por caracteres (maxSkillsPromptChars)
   └── Truncar si no cabe

3. INYECCIÓN EN PROMPT
   ├── formatSkillsForPrompt() → XML format
   ├── binary search para ajustar tamaño
   └── compactSkillPaths() → ~path → ~5-6 tokens

4. EJECUCIÓN (system-prompt.ts:33-39)
   "Before replying: scan <available_skills> <description> entries."
   - Si 1 skill aplica → leer SKILL.md
   - Si múltiples → elegir el más específico
   - Si ninguno → no leer
```

### Límites configurables

```typescript
// workspace.ts:95-99
DEFAULT_MAX_CANDIDATES_PER_ROOT = 300
DEFAULT_MAX_SKILLS_LOADED_PER_SOURCE = 200
DEFAULT_MAX_SKILLS_IN_PROMPT = 150
DEFAULT_MAX_SKILLS_PROMPT_CHARS = 30_000
DEFAULT_MAX_SKILL_FILE_BYTES = 256_000
```

---

## BANABOT: Motor de Skills

### Formato actual (context.py)

```markdown
# Skills

The following skills extend your capabilities. To use a skill, read its SKILL.md file using the read_file tool.
Skills with available="false" need dependencies installed first - you can try installing them with apt/brew.

## Available Skills

| Name | Description | Available |
|------|-------------|-----------|
| github | Interact with GitHub using the gh CLI | true |
| weather | Get weather info using wttr.in | true |
| ...
```

### Cómo funciona (simplificado)

```
1. SkillsLoader.load_skills()
   ├── Lee directorio skills/
   └── Parsea SKILL.md (frontmatter + contenido)

2. build_skills_summary()
   ├── Genera tabla markdown
   └── Muestra availability

3. INYECCIÓN EN PROMPT
   ├── Lista simple en system prompt
   └── Agent decide qué usar
```

### Código (skills.py ~80 líneas)

```python
class SkillsLoader:
    def __init__(self, workspace):
        self.workspace = workspace
        self.skills_dir = workspace / "skills"
    
    def get_always_skills(self) -> list[str]:
        """Skills que siempre se cargan."""
        return ["skill-creator"]  # solo 1
    
    def build_skills_summary(self) -> str:
        """Genera lista markdown."""
        ...
```

---

## COMPARACIÓN DETALLADA

### Skills de OpenCLAW (55)

```
1password              → Gestión de passwords
apple-notes            → Notas Apple
apple-reminders        → Recordatorios Apple
bear-notes             → Notas Bear
blogwatcher            → RSS feeds
blucli                 → Bluetooth
bluebubbles            → iMessage
camsnap               → Cámaras
canvas                → Canvas (UI)
clawhub               → Skill registry
coding-agent          → Agentes de código (284 líneas!) ⚡
discord               → Discord
eightctl              → Controlador Eight
food-order            → Comida
gemini               → Google Gemini
gh-issues            → GitHub Issues
gifgrep              → Buscar GIFs
github               → GitHub CLI
gog                  → Game platform
goplaces            → Places
healthcheck          → Health checks
himalaya            → Email CLI
imsg                → iMessage
mcporter            → Mcporter
model-usage          → Usage stats
nano-banana-pro     → Banana Pro
nano-pdf            → PDF
notion              → Notion
obsidian            → Obsidian
openai-image-gen    → DALL-E
openai-whisper      → Whisper
openhue             → Philips Hue
oracle              → Oracle
ordercli            → Orders
peekaboo            → Peekaboo
sag                 → SAG
session-logs        → Logs
skill-creator       → Crear skills
slack               → Slack
songsee            → Lyrics
sonoscli           → Sonos
spotify-player     → Spotify
summarize           → Resumir URLs
things-mac          → Things
tmux               → Tmux
trello             → Trello
video-frames       → Frames
voice-call         → Voz
wacli              → WA
weather            → Clima
xurl               → URL expander
```

### Skills de BanaBot (8)

```
clawhub              → (vacío, no implementado)
cron                 → Cron jobs (básico)
github               → GitHub CLI (48 líneas)
memory               → Memoria (vacío)
skill-creator       → Crear skills (básico)
summarize           → Resumir URLs (básico)
tmux                → Tmux (básico)
weather             → Clima (básico)
```

---

## ANÁLISIS: Por qué la diferencia importa

### OpenCLAW: Skills como "Herramientas Especializadas"

```
┌─────────────────────────────────────────────────────────────┐
│ EJEMPLO: coding-agent (284 LÍNEAS)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ## PTY Mode Required!                                      │
│ Coding agents (Codex, Claude Code, Pi) are interactive     │
│ terminal applications that need a pseudo-terminal.         │
│                                                             │
│ ## Bash Tool Parameters                                    │
│ | Parameter | Type | Description |                        │
│ | pty | boolean | Use for coding agents! |                │
│ | workdir | string | Working directory |                  │
│ | background | boolean | Run in background |             │
│                                                             │
│ ## Process Tool Actions                                    │
│ | Action | Description |                                  │
│ | list | List sessions |                                  │
│ | poll | Check if running |                               │
│ | log | Get output |                                      │
│                                                             │
│ ## The Pattern: workdir + background + pty                 │
│ bash pty:true workdir:~/project background:true ...        │
│                                                             │
│ ## Auto-Notify on Completion                               │
│ openclaw system event --text "Done: ..."                   │
│                                                             │
│ ## Learnings (Jan 2026)                                   │
│ - PTY is essential                                        │
│ - Git repo required                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### BanaBot: Skills Genéricos

```
┌─────────────────────────────────────────────────────────────┐
│ EJEMPLO: github (48 LÍNEAS)                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ # GitHub Skill                                             │
│                                                             │
│ Use the gh CLI to interact with GitHub.                    │
│                                                             │
│ ## Pull Requests                                           │
│ gh pr checks 55 --repo owner/repo                          │
│                                                             │
│ ## API for Advanced Queries                                 │
│ gh api repos/owner/repo/pulls/55 --jq '.title'             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## GAP ANALYSIS

| Área | OpenCLAW | BanaBot | Impacto |
|------|----------|---------|---------|
| Cantidad | 55 | 8 | ❌ No puedes hacer muchas tareas |
| Detail | 100-300 líneas | 20-50 líneas | ❌ Agent no sabe hacer cosas complejas |
| Formato | XML estructurado | Markdown simple | ❌ Menorparse |
| Filtros | Por workspace, plugin | No | ❌ Carga todo |
| Watch | Auto-reload | No | ❌ Cambios requieren restart |
| Límites | Chars, count, binary search | No | ❌ Prompt puede explotar |

---

## QUÉ HACER

### Nivel 1: Básico (FÁCIL)

```python
# Agregar más skills básicos:
- discord       → webhooks
- slack         → webhooks  
- notion        → API
- obsidian      → vault
- file-manager  → glob, grep, find
```

### Nivel 2: Medio (NECESARIO)

```python
# Mejorar skills existentes:
- github        → 48 → 150 líneas
- weather       → básico → completo
- summarize     → básico → con múltiples fuentes

# Agregar skills complejos:
- coding-agent  → 284 líneas como OpenCLAW
- web-research → búsqueda avanzada
```

### Nivel 3: Avanzado (SI QUIERES IGUALAR)

```python
# Implementar motor como OpenCLAW:
- formatSkillsForPrompt() → XML format
- Binary search para truncation
- Skill eligibility (config, env)
- File watcher para reload
- Max chars/limits configurables
```

---

## RECOMENDACIÓN

Para que BanaBot sea "menos tonto", **necesitas más skills y más detallados**:

| Prioridad | Skill | Descripción |
|-----------|-------|-------------|
| ALTA | coding-agent | Como OpenCLAW, 200+ líneas |
| ALTA | web-research | Google, scraping, síntesis |
| ALTA | file-manager | glob, grep, find, edit |
| MEDIA | discord | Webhooks, messages |
| MEDIA | slack | Webhooks, messages |
| MEDIA | notion | CRUD en Notion |
| MEDIA | obsidian | Vault management |
| BAJA | 10+ skills menores | расширение cobertura |

**El skill más importante es `coding-agent`** - permite delegar tareas complejas a otros agentes (Codex, Claude, etc.) sin que BanaBot tenga que saber hacerlo todo.

---

## RESUMEN VISUAL

```
OPENCLAW:
skills/
├── 55 skills/
│   ├── coding-agent/     → 284 líneas (PTYa, background, auto-notify)
│   ├── github/           → 200+ líneas
│   ├── discord/          → 200+ líneas
│   └── ...52 más
├── Motor: XML + binary search + filters + watch
└── Prompt: <available_skills>...</available_skills>

BANABOT:
skills/
├── 8 skills/
│   ├── github/           → 48 líneas
│   ├── weather/          → 30 líneas
│   └── ...6 más
├── Motor: Markdown simple
└── Prompt: ## Skills\n| name | description |
```

**Diferencia**: 55 vs 8 skills, 2500 vs 200 líneas de motor.

---

# PROPUESTA: Motor de Skills Incremental para BanaBot

## Concepto

No necesitas copiar a OpenCLAW. Necesitas un motor que te permita **agregar skills uno por uno**, cada uno agregando una "capa" de capacidad al bot.

```
┌─────────────────────────────────────────────────────────────┐
│                    MOTOR DE SKILLS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   skill_loader.py                                          │
│   ├── load_skills() → descubre todos los skills           │
│   ├── get_skill(name) → obtiene skill específico          │
│   ├── format_for_prompt() → formatea para LLM            │
│   └── watch_changes() → reload automático (futuro)       │
│                                                             │
│   skill_format.py                                          │
│   ├── Frontmatter (name, description, requires)            │
│   ├── Secciones (Usage, Examples, Tips)                   │
│   └── Validación                                          │
│                                                             │
│   skills/                                                  │
│   ├── _core/           → skills base (siempre cargados)   │
│   │   ├── coding-agent/                                   │
│   │   └── file-manager/                                   │
│   ├── _community/     → skills opcionales                 │
│   │   ├── github/                                        │
│   │   ├── weather/                                       │
│   │   └── ...                                            │
│   └── _registry/     → skills descargados                 │
│       └── (futuro: clawhub)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Formato de Skill Estándar

```yaml
---
name: github
description: "Interact with GitHub using gh CLI. Use for PRs, issues, repos."
emoji: "🐙"

# Qué binaries necesita (el motor verifica y avisa si faltan)
requires:
  bins: ["gh"]

# Cómo instalarlo si no existe
install:
  - kind: brew
    formula: gh
  - kind: apt
    package: gh

# Keywords para matching (el LLM usa esto para elegir skill)
keywords:
  - github
  - pr
  - issue
  - repo
  - commit
  - branch
---

# Usage

Usa `gh` para interacturar con GitHub.

## Pull Requests

```bash
# Ver estado de PR
gh pr status

# Ver checks de un PR
gh pr checks <num> --repo owner/repo
```

## Issues

```bash
# Listar issues
gh issue list --repo owner/repo

# Ver issue específico
gh issue view <num> --repo owner/repo
```

---

# Tips

- Siempre especifica `--repo owner/repo` cuando no estás en un git directory
- Usa `--json` para output estructurado
- Combina con `jq` para filtrar resultados
```

## Motor: skill_loader.py

```python
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import yaml
import re

@dataclass
class Skill:
    name: str
    description: str
    path: Path
    content: str
    frontmatter: dict
    keywords: list[str]
    requires: dict
    available: bool  # True si todas las dependencias existen

class SkillLoader:
    """Motor de skills simple y extensible."""
    
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self._cache: dict[str, Skill] = {}
    
    def load_all(self) -> dict[str, Skill]:
        """Carga todos los skills del directorio."""
        if self._cache:
            return self._cache
        
        skills = {}
        for skill_path in self.skills_dir.iterdir():
            if not skill_path.is_dir():
                continue
            
            skill_file = skill_path / "SKILL.md"
            if not skill_file.exists():
                continue
            
            skill = self._load_skill(skill_path, skill_file)
            if skill:
                skills[skill.name] = skill
        
        self._cache = skills
        return skills
    
    def _load_skill(self, path: Path, skill_file: Path) -> Optional[Skill]:
        """Carga un skill individual."""
        content = skill_file.read_text(encoding='utf-8')
        
        # Parse frontmatter
        frontmatter = {}
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                yaml_content = content[3:end]
                frontmatter = yaml.safe_load(yaml_content) or {}
        
        name = frontmatter.get('name', path.name)
        description = frontmatter.get('description', '')
        keywords = frontmatter.get('keywords', [])
        requires = frontmatter.get('requires', {})
        
        # Verificar disponibilidad
        available = self._check_availability(requires)
        
        return Skill(
            name=name,
            description=description,
            path=skill_file,
            content=content,
            frontmatter=frontmatter,
            keywords=keywords,
            requires=requires,
            available=available
        )
    
    def _check_availability(self, requires: dict) -> bool:
        """Verifica si las dependencias del skill están disponibles."""
        import shutil
        
        bins = requires.get('bins', [])
        for bin_name in bins:
            if not shutil.which(bin_name):
                return False
        return True
    
    def format_for_prompt(self, skills: dict[str, Skill]) -> str:
        """Formatea skills para inyección en prompt."""
        lines = ["<available_skills>"]
        
        for skill in skills.values():
            lines.append("  <skill>")
            lines.append(f"    <name>{skill.name}</name>")
            lines.append(f"    <description>{skill.description}</description>")
            if skill.keywords:
                lines.append(f"    <keywords>{', '.join(skill.keywords)}</keywords>")
            lines.append("  </skill>")
        
        lines.append("</available_skills>")
        
        # Agregar guía de uso
        lines.append("")
        lines.append("## Skills Usage")
        lines.append("Before replying: scan <available_skills> entries.")
        lines.append("- If 1 skill applies: read its SKILL.md, then follow it")
        lines.append("- If multiple apply: choose most specific")
        lines.append("- If none apply: don't read any")
        
        return "\n".join(lines)
    
    def get_skill_content(self, name: str) -> Optional[str]:
        """Obtiene el contenido de un skill específico."""
        skills = self.load_all()
        skill = skills.get(name)
        return skill.content if skill else None
```

## Cómo agregar un nuevo skill

```
1. Crear directorio: skills/new-skill/
2. Crear archivo: skills/new-skill/SKILL.md
3. Escribir frontmatter + contenido
4. Listo - el motor lo descubre automáticamente
```

Ejemplo: skills/coding-agent/SKILL.md

```yaml
---
name: coding-agent
description: "Delegate complex coding tasks to external agents (Codex, Claude, OpenCode)."
emoji: "🧩"
keywords:
  - code
  - program
  - build
  - refactor
  - pr
  - review
requires:
  bins: ["codex", "claude", "opencode"]
---

# Coding Agent

Use external coding agents for complex tasks.

## When to Use

- Building new features or apps
- Reviewing PRs
- Refactoring large codebases
- Iterative coding that needs exploration

## NOT for

- Simple one-liner fixes (just edit)
- Reading code (use read tool)
- Working in ~/workspace (never spawn agents there)

## Bash Tool

```bash
# With PTY (REQUIRED for interactive agents)
bash pty:true workdir:~/project command:"codex exec 'Your prompt'"

# Background mode
bash pty:true workdir:~/project background:true command:"codex exec --full-auto 'Task'"
```

## Process Tool (for background)

| Action | Description |
|--------|-------------|
| list | List running sessions |
| poll | Check if still running |
| log | Get output |
| write | Send to stdin |
| submit | Send + Enter |
| kill | Terminate |

## Examples

```bash
# Build a REST API
bash pty:true workdir:~/project background:true command:"codex --yolo exec 'Build REST API for todos'"

# Review PR
bash pty:true workdir:/tmp/review command:"codex review --base origin/main"
```

## Auto-Notify

Add to prompt for completion notification:

```
When done, run: banabot system event --text "Done: ..."
```

## Tips

- Always use pty:true - without it agents hang
- Codex needs a git repo - use mktemp -d && git init for scratch
- Use background for long tasks
- Monitor with process log
```

## Sistema de categorias (opcional)

```
skills/
├── _core/           → Skills fundamentales
│   ├── coding-agent/    (delegar a otros agentes)
│   ├── file-manager/   (glob, grep, find)
│   └── web-search/    (búsqueda web)
│
├── _integrations/   → Servicios externos
│   ├── github/
│   ├── slack/
│   ├── discord/
│   ├── notion/
│   └── obsidian/
│
├── _tools/         → Utilidades
│   ├── weather/
│   ├── summarize/
│   ├── translate/
│   └── cron/
│
└── _experimental/  → En desarrollo
    ├── voice/
    └── memory/
```

## Próximos pasos ( Roadmap )

| Fase | Skills | Descripción |
|------|--------|-------------|
| 1 (Ahora) | 3 | coding-agent, file-manager, web-search |
| 2 | +5 | github, weather, summarize, cron, memory |
| 3 | +5 | slack, discord, notion, obsidian, translate |
| 4 | +10 | Expansión según necesidad |

## Beneficios del enfoque

```
✓ Agregas skills sin modificar código del motor
✓ Cada skill es independiente
✓ Puedes probar skills sin afectar otros
✓ Comunidad puede contribuir skills
✓ Sistema crece orgánicamente
✓ No necesitas 55 skills de entrada
```

## Diferencia vs OpenCLAW

| Aspecto | OpenCLAW | Propuesta BanaBot |
|---------|----------|------------------|
| Skills | 55 (todos a la vez) | 3-8 (incremental) |
| Motor | 2500 líneas | 150 líneas |
| Formato | XML complejo | YAML + Markdown |
| Filtros | Avanzados | Básico |
| Watch | Sí | No (futuro) |
| Instalación | brew/apt/npm |brew/apt |

**Nosotros no necesitamos 55 skills. Necesitamos los correctos.**

Empieza con 3-5 skills bien diseñados y ve agregando según lo que necesites.
