# Guía de Desarrollo

## Requisitos

- Python 3.11+
- uv (recomendado) o pip
- Git

## Instalación con uv (Recomendado)

### 1. Crear entorno virtual

```bash
# Crear venv con Python 3.11+
uv venv

# Activar entorno
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate     # Windows
```

### 2. Instalar en modo desarrollo

```bash
# Instalar el paquete en modo editable
uv pip install -e .

# Instalar dependencias de desarrollo
uv pip install -e ".[dev]"
```

### 3. Verificar instalación

```bash
banabot --version
# 🍌 banabot v0.2.0
```

---

## Instalación con pip (Alternativa)

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate     # Windows

# Instalar en modo desarrollo
pip install -e ".[dev]"
```

---

## Flujo de Desarrollo

### Día a día

```bash
# 1. Activar entorno virtual (si no está activo)
source .venv/bin/activate

# 2. Hacer cambios en el código
vim banabot/cli/commands.py

# 3. Probar inmediatamente (sin reinstalar)
banabot status
banabot --help

# 4. Correr tests
pytest

# 5. Linting
ruff check banabot/
ruff format banabot/
```

### Agregar nuevas dependencias

Si agregas dependencias a `pyproject.toml`:

```bash
# Con uv
uv pip install -e .

# Con pip
pip install -e .
```

---

## Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `source .venv/bin/activate` | Activar entorno virtual |
| `deactivate` | Desactivar entorno virtual |
| `banabot --version` | Verificar instalación |
| `banabot status` | Ver estado de configuración |
| `pytest` | Correr tests |
| `ruff check banabot/` | Linting |
| `ruff format banabot/` | Formatear código |

---

## Estructura del Proyecto

```
banabot/
├── banabot/              # Código principal
│   ├── __init__.py
│   ├── cli/              # Comandos CLI
│   ├── agent/            # Lógica del agente
│   ├── channels/         # Integraciones de chat
│   ├── providers/        # Proveedores LLM
│   ├── config/           # Configuración
│   └── utils/            # Utilidades
├── tests/                # Tests
├── pyproject.toml        # Configuración del proyecto
└── .venv/                # Entorno virtual (no commitear)
```

---

## Publicar Nueva Versión

### 1. Actualizar versión

```bash
# Editar pyproject.toml
version = "0.3.0"

# Editar banabot/__init__.py
__version__ = "0.3.0"
```

### 2. Actualizar changelog

```bash
# Crear archivo de changelog
vim changelog/0.3.0.md

# Actualizar índice
vim CHANGELOG.md
```

### 3. Commit y tag

```bash
git add .
git commit -m "release: v0.3.0"
git tag -a v0.3.0 -m "🍌 banabot v0.3.0"
git push origin main --tags
```

### 4. Build y publicar

```bash
# Build
python -m build

# Subir a PyPI
twine upload dist/*
```

---

## Debugging

### Ver logs

```bash
# Habilitar logs debug
banabot agent --logs
```

### Probar imports

```bash
python -c "
from banabot import __version__, __logo__
from banabot.config.loader import get_config_path
print(f'Version: {__version__}')
print(f'Config: {get_config_path()}')
"
```

---

## Tips

- **Siempre usa entorno virtual** para aislar dependencias
- **Instala con `-e`** para que los cambios se reflejen sin reinstalar
- **Corre tests** antes de commit
- **Formatea con ruff** antes de commit
- **Actualiza changelog** con cada release
