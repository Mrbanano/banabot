import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

MAX_PROMPT_CHARS = 30_000


@dataclass
class Skill:
    name: str
    description: str
    path: Path
    content: str
    frontmatter: dict
    keywords: list[str] = field(default_factory=list)
    requires: dict = field(default_factory=dict)
    install: list[dict] = field(default_factory=list)
    available: bool = True
    emoji: str = ""


@dataclass
class ValidationResult:
    """Resultado de validación de un skill."""

    valid: bool
    errors: list[str]
    warnings: list[str]


class SkillValidationError(Exception):
    """Error de validación de skill."""

    pass


class SkillLoader:
    """Motor de skills v2 - formato XML para prompts."""

    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self._cache: dict[str, Skill] = {}

    def load_all(self, validate: bool = False) -> dict[str, Skill]:
        """Carga todos los skills del directorio."""
        if self._cache:
            return self._cache

        skills = {}
        for category in self._get_categories():
            category_path = self.skills_dir / category
            if not category_path.is_dir():
                continue

            for skill_path in category_path.iterdir():
                if not skill_path.is_dir():
                    continue

                skill_file = skill_path / "SKILL.md"
                if not skill_file.exists():
                    continue

                skill = self._load_skill(skill_path, skill_file)
                if skill:
                    if validate:
                        validation = self.validate_skill(skill)
                        if not validation.valid:
                            print(
                                f"⚠️  Skill '{skill.name}' has validation errors: {validation.errors}"
                            )
                        if validation.warnings:
                            print(f"⚡  Skill '{skill.name}' warnings: {validation.warnings}")

                    skills[skill.name] = skill

        self._cache = skills
        return skills

    def _get_categories(self) -> list[str]:
        """Categorías de skills (built-in + cualquier subdirectorio)."""
        base_categories = ["_core", "_integrations", "_tools"]

        # Agregar cualquier subdirectorio que exista en skills_dir
        if self.skills_dir.exists():
            for item in self.skills_dir.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    if item.name not in base_categories:
                        base_categories.append(item.name)

        return base_categories

    def validate_skill(self, skill: Skill) -> ValidationResult:
        """Valida la estructura de un skill."""
        errors = []
        warnings = []

        # Required: name
        if not skill.name or not skill.name.strip():
            errors.append("Missing or empty 'name' in frontmatter")

        # Required: description
        if not skill.description or not skill.description.strip():
            warnings.append("Missing or empty 'description' in frontmatter")

        # Recommended: keywords
        if not skill.keywords:
            warnings.append("Missing 'keywords' in frontmatter - skill may not be routable")

        # Validate metadata structure
        metadata = skill.frontmatter.get("metadata", {})
        if not metadata:
            warnings.append("Missing 'metadata' section in frontmatter")

        # Validate requires
        requires = skill.requires
        if requires:
            if not isinstance(requires, dict):
                errors.append("'metadata.openclaw.requires' must be a dictionary")
            else:
                bins = requires.get("bins", [])
                any_bins = requires.get("anyBins", [])
                if bins and not isinstance(bins, list):
                    errors.append("'requires.bins' must be a list")
                if any_bins and not isinstance(any_bins, list):
                    errors.append("'requires.anyBins' must be a list")

        # Validate install hints
        install = skill.install
        if install:
            if not isinstance(install, list):
                errors.append("'metadata.openclaw.install' must be a list")
            else:
                for idx, item in enumerate(install):
                    if not isinstance(item, dict):
                        warnings.append(f"install[{idx}] should be a dictionary")
                    elif "kind" not in item:
                        warnings.append(f"install[{idx}] missing 'kind' - may not be installable")

        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def _load_skill(self, path: Path, skill_file: Path) -> Optional[Skill]:
        """Carga un skill individual."""
        try:
            content = skill_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"❌ Skill file not found: {skill_file}")
            return None
        except PermissionError:
            print(f"❌ Permission denied reading: {skill_file}")
            return None
        except UnicodeDecodeError:
            print(f"❌ Invalid encoding: {skill_file}")
            return None
        except Exception as e:
            print(f"❌ Error reading {skill_file}: {e}")
            return None

        frontmatter = {}
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                yaml_content = content[3:end]
                try:
                    frontmatter = yaml.safe_load(yaml_content) or {}
                except yaml.YAMLError as e:
                    print(f"⚠️  YAML parse error in {skill_file.name}: {e}")
                    frontmatter = {}

        name = frontmatter.get("name", path.name)
        if not name:
            name = path.name

        description = frontmatter.get("description", "")

        metadata = frontmatter.get("metadata", {})
        openclaw_meta = metadata.get("openclaw", {})

        keywords = frontmatter.get("keywords", [])
        requires = openclaw_meta.get("requires", {})
        install = openclaw_meta.get("install", [])

        available = self._check_availability(requires)
        emoji = openclaw_meta.get("emoji", "")

        return Skill(
            name=name,
            description=description,
            path=skill_file,
            content=content,
            frontmatter=frontmatter,
            keywords=keywords,
            requires=requires,
            install=install,
            available=available,
            emoji=emoji,
        )

    def _check_availability(self, requires: dict) -> bool:
        """Verifica si las dependencias del skill están disponibles."""
        bins = requires.get("bins", [])
        any_bins = requires.get("anyBins", [])

        if bins:
            return all(shutil.which(b) for b in bins)
        elif any_bins:
            return any(shutil.which(b) for b in any_bins)
        return True

    def get_install_hints(self, skill: Skill) -> list[str]:
        """Genera hints de instalación para un skill no disponible."""
        if skill.available:
            return []

        hints = []
        install = skill.install
        requires = skill.requires

        if not install and not requires:
            hints.append(
                f"Skill '{skill.name}' requires dependencies but no install hints provided"
            )
            return hints

        for item in install:
            kind = item.get("kind", "")
            formula = item.get("formula", item.get("package", ""))
            label = item.get("label", "")

            if kind == "brew":
                cmd = f"brew install {formula}"
                hints.append(f"{label}: `{cmd}`")
            elif kind == "apt":
                cmd = f"sudo apt install {formula}"
                hints.append(f"{label}: `{cmd}`")
            elif kind == "npm":
                cmd = f"npm install -g {formula}"
                hints.append(f"{label}: `{cmd}`")
            elif kind == "pip":
                cmd = f"pip install {formula}"
                hints.append(f"{label}: `{cmd}`")
            else:
                if formula:
                    hints.append(f"{label}: install `{formula}` ({kind})")

        return hints

    def format_for_prompt(
        self,
        skills: Optional[dict[str, Skill]] = None,
        max_chars: int = MAX_PROMPT_CHARS,
    ) -> str:
        """Formatea skills para inyección en prompt (formato XML) con truncation."""
        if skills is None:
            skills = self.load_all()

        lines = ["<available_skills>"]

        # Primero skills disponibles, luego no disponibles
        available_skills = [s for s in skills.values() if s.available]
        unavailable_skills = [s for s in skills.values() if not s.available]

        for skill in available_skills:
            lines.extend(self._format_skill_xml(skill))

        # Skills no disponibles con hints de instalación
        for skill in unavailable_skills:
            lines.extend(self._format_skill_xml(skill, show_install=True))

        lines.append("</available_skills>")

        # Truncation si excede el límite
        result = "\n".join(lines)
        if len(result) > max_chars:
            # Binary search para ajustar
            result = self._truncate_skills(lines, max_chars)

        # Agregar instrucciones de uso
        result += "\n\n## Skills Usage"
        result += "\nBefore replying: scan <available_skills> entries."
        result += "\n- If 1 skill applies: read its SKILL.md, then follow it"
        result += "\n- If multiple apply: choose the most specific"
        result += "\n- If none apply: don't read any"

        # Agregar installation hints para skills no disponibles
        for skill in unavailable_skills:
            hints = self.get_install_hints(skill)
            if hints:
                result += f"\n\n## Install {skill.name}"
                for hint in hints:
                    result += f"\n- {hint}"

        return result

    def _format_skill_xml(self, skill: Skill, show_install: bool = False) -> list[str]:
        """Formatea un skill como XML."""
        lines = []
        lines.append("  <skill>")
        lines.append(f"    <name>{skill.name}</name>")

        # Emoji
        if skill.emoji:
            lines.append(f"    <emoji>{skill.emoji}</emoji>")

        lines.append(f"    <description>{skill.description}</description>")

        if skill.keywords:
            lines.append(f"    <keywords>{', '.join(skill.keywords)}</keywords>")

        # Available status
        if not skill.available:
            lines.append("    <available>false</available>")
            if show_install:
                hints = self.get_install_hints(skill)
                if hints:
                    lines.append(f"    <install_hints>{'; '.join(hints)}</install_hints>")

        lines.append("  </skill>")
        return lines

    def _truncate_skills(self, lines: list[str], max_chars: int) -> str:
        """Trunca skills usando binary search."""
        # Encontrar dónde empiezan los skills
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() == "<available_skills>":
                start_idx = i + 1
                break

        # Binary search
        low, high = 0, len(lines) - start_idx
        while low < high:
            mid = (low + high + 1) // 2
            test_lines = lines[: start_idx + mid] + ["</available_skills>"]
            if len("\n".join(test_lines)) <= max_chars:
                low = mid
            else:
                high = mid - 1

        # Aplicar truncation
        truncated_lines = lines[: start_idx + low]
        truncated_lines.append(
            f"  <!-- ... {len(lines) - start_idx - low} more skills truncated -->"
        )
        truncated_lines.append("</available_skills>")

        return "\n".join(truncated_lines)

    def get_skill_content(self, name: str) -> Optional[str]:
        """Obtiene el contenido de un skill específico."""
        skills = self.load_all()
        skill = skills.get(name)
        return skill.content if skill else None

    def get_skill(self, name: str) -> Optional[Skill]:
        """Obtiene un skill específico."""
        skills = self.load_all()
        return skills.get(name)

    def reload(self) -> dict[str, Skill]:
        """Recarga todos los skills (invalida cache)."""
        self._cache = {}
        return self.load_all()


@dataclass
class SkillMatch:
    """Resultado de matching de un skill."""

    skill: Optional[str]
    confidence: float
    reason: str


class SkillRouter:
    """Router que decide qué skill usar basándose en keywords."""

    def __init__(self, loader: SkillLoader):
        self.loader = loader
        self._skills: Optional[dict[str, Skill]] = None

    @property
    def skills(self) -> dict[str, Skill]:
        if self._skills is None:
            self._skills = self.loader.load_all()
        return self._skills

    def route(self, message: str) -> SkillMatch:
        """
        Analiza un mensaje y decide qué skill usar.

        Args:
            message: Mensaje del usuario

        Returns:
            SkillMatch con el skill seleccionado, confianza y razón
        """
        message_lower = message.lower()

        # Scoring por keywords
        scores: dict[str, float] = {}

        for name, skill in self.skills.items():
            score = 0.0
            for keyword in skill.keywords:
                if keyword.lower() in message_lower:
                    score += 1.0

            if score > 0:
                scores[name] = score

        if not scores:
            return SkillMatch(
                skill=None, confidence=0.0, reason="No skill matches found - general conversation"
            )

        # Seleccionar el mejor scoring
        best_skill = max(scores.items(), key=lambda x: x[1])[0]
        best_score = scores[best_skill]

        # Confidence basada en score
        confidence = min(best_score / 3.0, 1.0)

        if confidence < 0.1:
            return SkillMatch(
                skill=None, confidence=0.0, reason="Low confidence - might be general conversation"
            )

        return SkillMatch(
            skill=best_skill,
            confidence=confidence,
            reason=f"Matched {int(best_score)} keywords for skill '{best_skill}'",
        )

    def route_json(self, message: str) -> str:
        """Retorna el resultado como JSON."""
        match = self.route(message)
        return json.dumps(
            {"skill": match.skill, "confidence": match.confidence, "reason": match.reason}
        )
