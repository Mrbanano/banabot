# Plan de Rebranding: nanobot → banobot

## Resumen Ejecutivo

Este documento describe el proceso completo para migrar el proyecto `nanobot` a `banobot`, incluyendo consideraciones legales, técnicas y éticas.

---

## 1. Análisis de Licencia

### Licencia Actual: MIT License

```
MIT License
Copyright (c) 2025 nanobot contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

### Lo que permite la licencia MIT:
- ✅ Usar el código para cualquier propósito (comercial o no)
- ✅ Modificar el código
- ✅ Distribuir copias
- ✅ Cambiar el nombre del proyecto
- ✅ Sublicenciar
- ✅ Vender copias

### Lo que requiere la licencia MIT:
- ⚠️ Incluir el aviso de copyright original
- ⚠️ Incluir la licencia MIT en todas las copias sustanciales

### Conclusión Legal:
**Sí es posible hacer el rebranding completo**. La licencia MIT es la más permisiva. Solo debemos:
1. Mantener el archivo LICENSE original con atribución a "nanobot contributors"
2. Agregar atribución adicional en README o archivo de créditos

---

## 2. Sobre los Contribuidores (Ética y Buenas Prácticas)

### ¿Qué hacer con los contribuidores originales?

**Recomendación estándar para forks:**

1. **Mantener la atribución original** - Los contribuidores del proyecto original merecen crédito por su trabajo.

2. **Opciones para el README:**

```markdown
## Agradecimientos

**banobot** es un fork de [nanobot](https://github.com/HKUDS/nanobot), 
un proyecto de código abierto desarrollado por la comunidad.

Agradecemos a todos los contribuidores originales de nanobot:
<a href="https://github.com/HKUDS/nanobot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HKUDS/nanobot&max=100&columns=12" />
</a>
```

3. **Archivo CREDITS.md (recomendado):**

```markdown
# Créditos

banobot es un fork de nanobot (https://github.com/HKUDS/nanobot)

## Contribuidores Originales
Este proyecto no sería posible sin el trabajo de los contribuidores de nanobot.
Ver lista completa: https://github.com/HKUDS/nanobot/graphs/contributors

## Licencia Original
MIT License - Copyright (c) 2025 nanobot contributors
```

4. **NO eliminar** la sección de contribuidores, solo adaptarla.

### ¿Por qué es importante?

- **Ética**: El código abierto vive de la colaboración
- **Legal**: La licencia MIT requiere mantener avisos de copyright
- **Comunidad**: Genera buena reputación y confianza
- **Historia**: Preserva la proveniencia del código

---

## 3. Alcance del Rebranding

### Estadísticas Actuales
| Métrica | Valor |
|---------|-------|
| Ocurrencias de "nanobot" | ~512 |
| Archivos Python afectados | 55 |
| Archivos de documentación | ~20 |
| Config paths | ~/.nanobot |
| Env variables | NANOBOT_* |
| CLI command | nanobot |

### Áreas a Modificar

#### A. Código Python (Imports y Referencias)
```
nanobot/ → banobot/
├── agent/
├── bus/
├── channels/
├── cli/
├── config/
├── cron/
├── heartbeat/
├── providers/
├── session/
├── skills/
└── utils/
```

#### B. Configuración del Paquete
- `pyproject.toml`: nombre, scripts, packages
- CLI command: `nanobot` → `banobot`

#### C. Rutas del Sistema
- `~/.nanobot` → `~/.banobot`
- Environment: `NANOBOT_*` → `BANOBOT_*`

#### D. Documentación
- `README.md`
- `SECURITY.md`
- `CHANGELOG.md`
- `workspace/*.md`
- `nanobot/skills/**/*.md`

#### E. Assets
- `nanobot_logo.png` → `banobot_logo.png`
- `nanobot_arch.png` → `banobot_arch.png`

#### F. Tests y Scripts
- `tests/*.py`
- `tests/*.sh`
- `core_agent_lines.sh`

---

## 4. Plan de Ejecución por Fases

### FASE 1: Preparación (Sin cambios de código)

**Objetivo**: Documentar y preparar el entorno.

| Tarea | Archivo | Descripción |
|-------|---------|-------------|
| 1.1 | `CREDITS.md` | Crear archivo de créditos con atribución |
| 1.2 | `LICENSE` | Actualizar copyright manteniendo original |
| 1.3 | Backup | Crear tag/branch de respaldo antes de cambios |

**Comandos:**
```bash
git tag pre-rebrand-backup
git checkout -b rebrand-banobot
```

---

### FASE 2: Renombrar Directorio Principal

**Objetivo**: Cambiar `nanobot/` → `banobot/`

| Tarea | Descripción |
|-------|-------------|
| 2.1 | Renombrar directorio `nanobot/` → `banobot/` |
| 2.2 | Actualizar `pyproject.toml` packages |

**Comandos:**
```bash
git mv nanobot banobot
```

---

### FASE 3: Actualizar pyproject.toml

**Archivo**: `pyproject.toml`

**Cambios:**
```toml
# ANTES
[project]
name = "nanobot-ai"
version = "0.1.4"
authors = [{name = "nanobot contributors"}]

[project.scripts]
nanobot = "nanobot.cli.commands:app"

[tool.hatch.build.targets.wheel]
packages = ["nanobot"]

[tool.hatch.build.targets.wheel.sources]
"nanobot" = "nanobot"

# DESPUÉS
[project]
name = "banobot-ai"
version = "0.1.4"
authors = [{name = "banobot contributors"}]

[project.scripts]
banobot = "banobot.cli.commands:app"

[tool.hatch.build.targets.wheel]
packages = ["banobot"]

[tool.hatch.build.targets.wheel.sources]
"banobot" = "banobot"
```

---

### FASE 4: Actualizar Imports (Python)

**Objetivo**: Reemplazar todos los imports `from nanobot` → `from banobot`

**Archivos afectados**: ~55 archivos Python

**Estrategia**: Usar `find + sed` para reemplazo masivo

```bash
# Reemplazo en archivos Python
find banobot -name "*.py" -exec sed -i '' 's/from nanobot/from banobot/g' {} \;
find banobot -name "*.py" -exec sed -i '' 's/import nanobot/import banobot/g' {} \;

# Reemplazo en tests
find tests -name "*.py" -exec sed -i '' 's/from nanobot/from banobot/g' {} \;
find tests -name "*.py" -exec sed -i '' 's/import nanobot/import banobot/g' {} \;
```

---

### FASE 5: Actualizar Rutas de Configuración

**Objetivo**: Cambiar `~/.nanobot` → `~/.banobot`

**Archivos clave:**
- `banobot/config/loader.py`
- `banobot/config/schema.py`
- `banobot/utils/helpers.py`
- `banobot/cli/commands.py`
- `banobot/session/manager.py`
- `banobot/channels/*.py`
- `banobot/skills/clawhub/SKILL.md`
- `banobot/skills/tmux/SKILL.md`

**Reemplazos:**
```bash
# Rutas de configuración
find . -name "*.py" -exec sed -i '' 's/\.nanobot/.banobot/g' {} \;
find . -name "*.md" -exec sed -i '' 's/\.nanobot/.banobot/g' {} \;

# Variables de entorno
find . -name "*.py" -exec sed -i '' 's/NANOBOT_/BANOBOT_/g' {} \;
find . -name "*.md" -exec sed -i '' 's/NANOBOT_/BANOBOT_/g' {} \;
```

---

### FASE 6: Actualizar Documentación

**Objetivo**: Rebranding de README.md y demás documentación

**Archivos:**
- `README.md` (principal)
- `SECURITY.md`
- `CHANGELOG.md`
- `workspace/TOOLS.md`
- `workspace/AGENTS.md`
- `workspace/USER.md`
- `workspace/SOUL.md`
- `workspace/HEARTBEAT.md`
- `workspace/memory/MEMORY.md`

**Cambios en README.md:**
1. Título: "nanobot" → "banobot"
2. Descripción del proyecto
3. Links de GitHub (HKUDS/nanobot → nuevo repo)
4. Sección de contribuidores (ver sección 2)
5. Badges y URLs

**Nota**: Mantener referencias al proyecto original donde sea apropiado.

---

### FASE 7: Assets y Archivos Especiales

**Objetivo**: Actualizar imágenes y archivos de configuración

| Tarea | Descripción |
|-------|-------------|
| 7.1 | Renombrar `nanobot_logo.png` → `banobot_logo.png` |
| 7.2 | Renombrar `nanobot_arch.png` → `banobot_arch.png` |
| 7.3 | Actualizar referencias en README.md |
| 7.4 | Actualizar `bridge/package.json` |
| 7.5 | Actualizar `docker-compose.yml` |
| 7.6 | Actualizar `.claude/settings.local.json` |

---

### FASE 8: Tests y Validación

**Objetivo**: Verificar que todo funciona después del rebranding

| Tarea | Comando |
|-------|---------|
| 8.1 Reinstalar paquete | `pip install -e .` |
| 8.2 Verificar CLI | `banobot --help` |
| 8.3 Correr tests | `pytest tests/` |
| 8.4 Linting | `ruff check banobot/` |
| 8.5 Probar imports | `python -c "from banobot import ..."` |

---

### FASE 9: Commit Final

**Objetivo**: Consolidar todos los cambios

```bash
git add -A
git commit -m "refactor: rebrand nanobot to banobot

- Rename package from nanobot-ai to banobot-ai
- Change CLI command from 'nanobot' to 'banobot'
- Update config path from ~/.nanobot to ~/.banobot
- Update env vars from NANOBOT_* to BANOBOT_*
- Add CREDITS.md with attribution to original contributors
- Keep MIT license with proper attribution

Fork of: https://github.com/HKUDS/nanobot"
```

---

## 5. Checklist de Verificación

### Pre-commit
- [ ] Crear tag de respaldo
- [ ] Crear rama de rebranding
- [ ] Documentar créditos

### Código
- [ ] Directorio renombrado `nanobot/` → `banobot/`
- [ ] Imports actualizados (55 archivos)
- [ ] pyproject.toml actualizado
- [ ] CLI command funciona: `banobot --help`

### Configuración
- [ ] Rutas ~/.nanobot → ~/.banobot
- [ ] Env vars NANOBOT_* → BANOBOT_*
- [ ] Variables en skills actualizadas

### Documentación
- [ ] README.md actualizado con créditos
- [ ] SECURITY.md actualizado
- [ ] CHANGELOG.md actualizado
- [ ] Workspace docs actualizados

### Assets
- [ ] Logo renombrado
- [ ] Diagrama renombrado
- [ ] Referencias actualizadas

### Tests
- [ ] Tests pasan
- [ ] Linting pasa
- [ ] Instalación funciona

---

## 6. Consideraciones Adicionales

### Migración de Usuarios Existentes

Si hay usuarios con configuración existente en `~/.nanobot`:

```bash
# Script de migración sugerido
#!/bin/bash
if [ -d ~/.nanobot ]; then
    echo "Migrando configuración de nanobot a banobot..."
    mv ~/.nanobot ~/.banobot
    echo "Migración completada."
fi
```

### Compatibilidad con Configuración Existente

Opción: Mantener compatibilidad con `~/.nanobot` temporalmente:

```python
# En config/loader.py
def get_config_path() -> Path:
    # Prioridad: nueva ubicación → ubicación antigua
    new_path = Path.home() / ".banobot" / "config.json"
    old_path = Path.home() / ".nanobot" / "config.json"
    
    if new_path.exists():
        return new_path
    if old_path.exists():
        return old_path
    return new_path  # Default para nuevos usuarios
```

### PyPI Publishing

Después del rebranding:
1. Registrar nuevo paquete `banobot-ai` en PyPI
2. El paquete `nanobot-ai` original sigue existiendo (no eliminar)
3. Considerar agregar nota en README de nanobot-ai apuntando al fork

---

## 7. Timeline Estimado

| Fase | Duración |
|------|----------|
| Fase 1: Preparación | 15 min |
| Fase 2: Renombrar directorio | 5 min |
| Fase 3: pyproject.toml | 10 min |
| Fase 4: Imports Python | 15 min |
| Fase 5: Rutas de config | 20 min |
| Fase 6: Documentación | 30 min |
| Fase 7: Assets | 10 min |
| Fase 8: Tests y validación | 15 min |
| Fase 9: Commit | 5 min |
| **Total** | ~2 horas |

---

## 8. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Tests fallan después del rebrand | Media | Correr tests antes de commit |
| Imports rotos | Alta | Usar find+sed exhaustivo |
| Documentación inconsistente | Media | Revisar manualmente archivos clave |
| Conflictos con repo original | Baja | Fork limpio, mantener atribución |
| Usuarios confundidos | Media | Documentar migración claramente |

---

## 9. Post-Rebranding

### Tareas siguientes:
1. Publicar en PyPI como `banobot-ai`
2. Configurar CI/CD para el nuevo repo
3. Actualizar documentación en línea
4. Comunicar a usuarios (si aplica)
5. Crear release inicial de banobot

---

## 10. Versionado e Historial de Git

### Decisión: NO reescribir historial de Git

**¿Por qué no reescribir el historial?**

| Razón | Explicación |
|-------|-------------|
| **Destructivo** | Requiere force push, rompe todos los clones existentes |
| **Complejo** | Requiere `git filter-branch` o `git-filter-repo` |
| **Riesgoso** | Puede perder commits, tags, o referencias |
| **Innecesario** | CHANGELOG.md documenta correctamente las versiones |
| **Práctica común** | Muchos forks de OSS mantienen el historial original |

### Versionado Adoptado

```
v0.0.1 - Nacimiento de banobot (fork + rebranding)
v0.1.0 - Multi-provider web search system
v0.2.0 - CLI interactivo mejorado + branding completo
```

### Dónde se define la versión

| Archivo | Contenido |
|---------|-----------|
| `pyproject.toml` | `version = "0.2.0"` |
| `banobot/__init__.py` | `__version__ = "0.2.0"` |
| `CHANGELOG.md` | Documentación de releases |

### Mapeo de Commits a Versiones

| Versión | Commit | Descripción |
|---------|--------|-------------|
| 0.0.1 | dc3b61e, b8dbc7e, b35c7f2 | Fork + rebranding inicial |
| 0.1.0 | 278cdbc | Multi-provider web search |
| 0.2.0 | b3f2641 | CLI interactivo + branding |

> **Nota**: El historial de git muestra commits del nanobot original. Esto es **intencional y correcto** - preserva la proveniencia del código y los créditos a los autores originales.

---

**Documento creado**: 2026-02-19
**Autor**: Equipo banobot
**Basado en**: nanobot (https://github.com/HKUDS/nanobot)
