"""Heartbeat tool for managing periodic tasks."""

from pathlib import Path
from typing import Any

from loguru import logger

from banabot.agent.tools.base import Tool


class HeartbeatTool(Tool):
    """Tool to manage heartbeat tasks (for dynamic/search-based periodic tasks).

    Use this for tasks that need to SEARCH/EVALUATE content.
    For scheduled tasks with specific times, use the 'cron' tool instead.
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._file = workspace / "HEARTBEAT.md"

    @property
    def name(self) -> str:
        return "heartbeat"

    @property
    def description(self) -> str:
        return """Manage heartbeat tasks for dynamic periodic actions.

Actions:
- read: Read current heartbeat tasks
- add: Add a new task (for dynamic/search-based tasks)
- remove: Remove a task by line number
- list: List current tasks (same as read)
- clear: Remove all tasks

When to use HEARTBEAT vs CRON:
- HEARTBEAT: Search/evaluate content, monitor without fixed schedule
- CRON: Specific time, same action repeatedly (use cron tool instead)"""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "add", "remove", "list", "clear"],
                    "description": "Action to perform",
                },
                "task": {
                    "type": "string",
                    "description": "Task to add (for add action)",
                },
                "line": {
                    "type": "integer",
                    "description": "Line number to remove (for remove action)",
                },
            },
            "required": ["action"],
        }

    async def execute(
        self,
        action: str,
        task: str = "",
        line: int | None = None,
        **kwargs: Any,
    ) -> str:
        if action in ("read", "list"):
            return self._read_tasks()
        elif action == "add":
            return self._add_task(task)
        elif action == "remove":
            return self._remove_task(line)
        elif action == "clear":
            return self._clear_tasks()
        return f"Unknown action: {action}"

    def _get_tasks_section(self) -> tuple[str, int]:
        """Extract the tasks section from the file."""
        if not self._file.exists():
            return "", -1

        content = self._file.read_text()
        lines = content.split("\n")

        in_tasks = False
        task_lines = []
        start_idx = 0

        for i, line in enumerate(lines):
            if line.strip() == "## Tasks":
                in_tasks = True
                start_idx = i + 1
                continue
            if in_tasks and line.startswith("## "):
                break
            if in_tasks:
                task_lines.append(line)

        return "\n".join(task_lines).strip(), start_idx

    def _read_tasks(self) -> str:
        """Read current tasks."""
        if not self._file.exists():
            return "No heartbeat tasks. Create one with 'add'."

        tasks, _ = self._get_tasks_section()
        if not tasks:
            return "No heartbeat tasks. Add one with 'add'."

        task_lines = [
            line for line in tasks.split("\n") if line.strip() and not line.strip().startswith("#")
        ]
        if not task_lines:
            return "No heartbeat tasks."

        result = "Current heartbeat tasks:\n"
        for i, line in enumerate(task_lines, 1):
            result += f"{i}. {line.strip()}\n"
        return result

    def _add_task(self, task: str) -> str:
        """Add a new task."""
        if not task:
            return "Error: task is required"

        if not self._file.exists():
            return f"Error: {self._file} not found"

        content = self._file.read_text()
        lines = content.split("\n")

        in_tasks = False
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip() == "## Tasks":
                in_tasks = True
                insert_idx = i + 1
                continue
            if in_tasks and line.startswith("## "):
                insert_idx = i
                break

        if insert_idx == 0:
            return "Error: Could not find ## Tasks section"

        new_lines = lines[:insert_idx] + [f"- {task}"] + lines[insert_idx:]
        self._file.write_text("\n".join(new_lines))

        logger.info(f"Heartbeat: added task '{task}'")
        return f"Added heartbeat task: '{task}'"

    def _remove_task(self, line: int | None) -> str:
        """Remove a task by line number."""
        if line is None or line < 1:
            return "Error: line number required (use 'list' to see line numbers)"

        if not self._file.exists():
            return "Error: no heartbeat file"

        tasks, start_idx = self._get_tasks_section()
        if not tasks:
            return "No tasks to remove"

        task_lines = [t for t in tasks.split("\n") if t.strip() and not t.strip().startswith("#")]

        if line > len(task_lines):
            return f"Error: line {line} out of range (1-{len(task_lines)})"

        removed = task_lines[line - 1]
        task_lines.pop(line - 1)

        content = self._file.read_text()
        lines = content.split("\n")

        new_content = lines[:start_idx] + task_lines + lines[start_idx + len(tasks.split("\n")) :]
        self._file.write_text("\n".join(new_content))

        logger.info(f"Heartbeat: removed task '{removed}'")
        return f"Removed task: '{removed}'"

    def _clear_tasks(self) -> str:
        """Clear all tasks."""
        if not self._file.exists():
            return "Error: no heartbeat file"

        content = self._file.read_text()
        lines = content.split("\n")

        in_tasks = False
        new_lines = []
        for line in lines:
            if line.strip() == "## Tasks":
                in_tasks = True
                new_lines.append(line)
                continue
            if in_tasks and line.startswith("## "):
                in_tasks = False
            if in_tasks and line.strip() and not line.startswith("#"):
                continue
            new_lines.append(line)

        self._file.write_text("\n".join(new_lines))
        logger.info("Heartbeat: cleared all tasks")
        return "Cleared all heartbeat tasks"
