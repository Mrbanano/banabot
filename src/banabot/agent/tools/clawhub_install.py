"""ClawHub installation tool for the agent."""

import json
import shutil
from pathlib import Path
from typing import Any

from banabot.agent.tools.base import Tool


class ClawHubInstallTool(Tool):
    """
    Tool to install skills from ClawHub registry.

    This tool handles the installation properly, avoiding the nested
    skills/ directory issue by using --dir .
    """

    def __init__(self, workspace: Path):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "clawhub_install"

    @property
    def description(self) -> str:
        return """Install or update a skill from ClawHub registry.

Installs to the correct location automatically.
- Searches for skills
- Installs to workspace/skills/
- Handles directory structure correctly

Use this instead of running clawhub CLI manually."""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["install", "update", "search", "list"],
                    "description": "Action to perform",
                },
                "skill": {
                    "type": "string",
                    "description": "Skill name to install/update (for install/update actions)",
                },
                "version": {
                    "type": "string",
                    "description": "Specific version to install (optional)",
                },
                "registry": {
                    "type": "string",
                    "description": "Custom registry URL (optional)",
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for search action)",
                },
            },
            "required": ["action"],
        }

    async def execute(
        self,
        action: str,
        skill: str | None = None,
        version: str | None = None,
        registry: str | None = None,
        query: str | None = None,
    ) -> str:
        """Execute clawhub action."""

        if action == "search":
            return await self._search(query or skill or "")
        elif action == "list":
            return await self._list()
        elif action in ("install", "update"):
            if not skill:
                return json.dumps({"error": "skill parameter required for install/update"})
            return await self._install_or_update(action, skill, version, registry)
        else:
            return json.dumps({"error": f"Unknown action: {action}"})

    async def _search(self, query: str) -> str:
        """Search for skills."""
        import asyncio

        if not query:
            return json.dumps({"error": "query parameter required for search"})

        proc = await asyncio.create_subprocess_exec(
            "clawhub",
            "search",
            query,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            return json.dumps({"error": stderr.decode() or "Search failed"})

        results = []
        for line in stdout.decode().strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("-"):
                # Parse: skill-name v1.0.0  Description  (score)
                parts = line.split()
                if len(parts) >= 3:
                    results.append(
                        {
                            "raw": line,
                        }
                    )

        return json.dumps(
            {
                "query": query,
                "results": results,
                "hint": "Copy the skill name and use action=install to install it",
            },
            indent=2,
        )

    async def _list(self) -> str:
        """List installed skills."""
        skills_dir = self.workspace / "skills"
        if not skills_dir.exists():
            return json.dumps({"skills": []})

        installed = []
        for category in skills_dir.iterdir():
            if not category.is_dir() or category.name.startswith("."):
                continue
            for skill_dir in category.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    installed.append(
                        {
                            "name": skill_dir.name,
                            "category": category.name,
                            "path": str(skill_dir.relative_to(self.workspace)),
                        }
                    )

        return json.dumps({"skills": installed}, indent=2)

    async def _install_or_update(
        self,
        action: str,
        skill: str,
        version: str | None = None,
        registry: str | None = None,
    ) -> str:
        """Install or update a skill."""
        import asyncio

        skills_dir = self.workspace / "skills"
        skills_dir.mkdir(exist_ok=True)

        # Build command
        # NOTE: Don't use --dir . - it creates nested structure
        # Instead, run from workspace and let it install to ./skills/
        # Then we'll fix the location
        cmd = ["clawhub", action, skill]

        if version:
            cmd.extend(["--version", version])
        if registry:
            cmd.extend(["--registry", registry])

        # Run from workspace root
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        output = stdout.decode() + stderr.decode()

        if proc.returncode != 0:
            return json.dumps(
                {
                    "action": action,
                    "skill": skill,
                    "success": False,
                    "error": output,
                    "hint": "Make sure you're running from workspace with skills/ folder",
                }
            )

        # Find where the skill was installed
        # ClawHub installs to ./skills/<skill-name> by default
        nested = self.workspace / "skills" / skill
        direct = self.workspace / skill

        installed_path = None

        # Check if installed to skills/<skill>/
        if nested.exists():
            # Move to correct category (default: _tools)
            target = skills_dir / "_community" / skill
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(nested), str(target))
            installed_path = str(target)

        # Check if installed to workspace/<skill>/
        elif direct.exists():
            # Move to skills/_community/
            target = skills_dir / "_community" / skill
            target.parent.mkdir(parents=True, exist_ok=True)

            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(direct), str(target))
            installed_path = str(target)

        else:
            # Already exists in correct location?
            for cat in ["_core", "_integrations", "_tools", "_community"]:
                existing = skills_dir / cat / skill
                if existing.exists():
                    installed_path = str(existing)
                    break

        return json.dumps(
            {
                "action": action,
                "skill": skill,
                "success": True,
                "output": output.strip(),
                "installed_to": installed_path,
                "hint": "Skill loaded automatically - no restart needed",
            },
            indent=2,
        )
