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

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_commands.py

# Con coverage
pytest --cov=banabot tests/

# Tests de CLI
pytest tests/test_cli_input.py tests/test_commands.py -v
```

### Estructura de Tests

Los tests están en `tests/` y siguen naming conventions:

```
tests/
├── test_commands.py        # Tests de CLI commands
├── test_cli_input.py      # Tests de input interactivo
├── test_email_channel.py  # Tests de canales
├── test_tool_validation.py
└── test_consolidate_offset.py
```

### Patrones Comunes

#### 1. Testing de CLI con Typer

```python
from typer.testing import CliRunner
from banabot.cli.commands import app

runner = CliRunner()

def test_command():
    result = runner.invoke(app, ["command"], input="input\n")
    assert result.exit_code == 0
    assert "expected output" in result.stdout
```

#### 2. Mocking de paths

```python
from unittest.mock import patch
from pathlib import Path
import shutil

@pytest.fixture
def mock_paths():
    with patch("banabot.config.loader.get_config_path") as mock_cp, \
         patch("banabot.config.loader.save_config") as mock_sc:
        
        test_dir = Path("./test_data")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        test_dir.mkdir()
        
        mock_cp.return_value = test_dir / "config.json"
        
        yield test_dir
        
        if test_dir.exists():
            shutil.rmtree(test_dir)
```

#### 3. Testing async

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

#### 4. Mocking con patch

```python
from unittest.mock import patch, MagicMock

def test_with_mock():
    with patch("module.function") as mock_func:
        mock_func.return_value = "mocked"
        # test code
```

### Crear Nuevos Tests

1. **Nombrar archivo**: `test_<modulo>.py`
2. **Nombrar funciones**: `test_<descripcion>`
3. **Usar fixtures** para setup/teardown
4. **Assert claros** con mensajes descriptivos
5. **Aislar** cada test (no depende de orden)

### Ejemplo: Test de config_wizard

```python
import pytest
from typer.testing import CliRunner
from banabot.cli.commands import app
from banabot.config.schema import Config

runner = CliRunner()

def test_model_specs():
    """Verify MODEL_SPECS contains correct token limits."""
    from banabot.cli.config_wizard import MODEL_SPECS
    
    assert "anthropic/claude-opus-4-5" in MODEL_SPECS
    assert MODEL_SPECS["anthropic/claude-opus-4-5"]["max_tokens"] == 80000

def test_temperature_presets():
    """Verify temperature presets are correctly defined."""
    from banabot.cli.config_wizard import TEMPERATURE_PRESETS
    
    assert "creative" in TEMPERATURE_PRESETS
    assert TEMPERATURE_PRESETS["creative"][1] == 0.8
    assert TEMPERATURE_PRESETS["balanced"][1] == 0.4
    assert TEMPERATURE_PRESETS["concise"][1] == 0.2
```
