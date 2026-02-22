# BanaBot v2 Skills

Motor de skills con formato XML para prompts.

## Estructura

```
v2/skills/
├── _core/           → Skills fundamentales
│   └── file-manager/
├── _integrations/  → Servicios externos
│   ├── obsidian/
│   └── spotify/
└── _tools/         → Utilidades
    └── gifgrep/
```

## Uso

```python
from banabot.v2.skills.skill_loader import SkillLoader

loader = SkillLoader(Path("src/banabot/v2/skills"))

# Cargar todos
skills = loader.load_all()

# Formatear para prompt (XML)
prompt_section = loader.format_for_prompt(skills)

# Obtener skill específico
content = loader.get_skill_content("github")
```

## Formato de Skill

```yaml
---
name: skill-name
description: "Description for the LLM"
keywords: [keyword1, keyword2]
metadata:
  openclaw:
    emoji: "🎯"
    requires:
      bins: ["required-binary"]
    install:
      - id: brew
        kind: brew
        formula: binary-name
        bins: ["binary-name"]
        label: "Install (brew)"
---

# Skill Content

Your skill documentation here.
```

## Categorías

- `_core/`: Skills fundamentales (file-manager, coding-agent, etc.)
- `_integrations/`: Servicios externos (github, slack, notion, obsidian, spotify)
- `_tools/`: Utilidades (weather, summarize, gifgrep, cron)
