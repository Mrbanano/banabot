"""Skill router tool for the agent."""

import json
from typing import Any

from banabot.agent.tools.base import Tool
from banabot.v2.skills.skill_loader import SkillLoader, SkillMatch


class SkillRouterTool(Tool):
    """
    Tool that helps the LLM decide which skill to use based on keywords.

    The LLM can call this tool to get suggestions on which skill matches
    a user's message, with confidence scores and reasoning.
    """

    def __init__(self, skill_loader: SkillLoader):
        self.loader = skill_loader
        self._router = None

    @property
    def router(self) -> "InternalSkillRouter":
        """Lazy load the router."""
        if self._router is None:
            self._router = InternalSkillRouter(self.loader)
        return self._router

    @property
    def name(self) -> str:
        return "skill_router"

    @property
    def description(self) -> str:
        return """Analyze a message and suggest which skill to use based on keywords.
        
Returns the best matching skill with confidence score, plus top-k alternatives.
Use this when uncertain which skill applies to the user's request.
If no skill matches, returns null - proceed with general conversation."""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The user's message to analyze for skill matching",
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top matches to return (default 3, max 5)",
                    "minimum": 1,
                    "maximum": 5,
                    "default": 3,
                },
            },
            "required": ["message"],
        }

    async def execute(self, message: str, top_k: int = 3) -> str:
        """
        Execute the skill router.

        Args:
            message: The user's message to analyze
            top_k: Number of top matches to return

        Returns:
            JSON string with skill suggestions
        """
        if not message or not message.strip():
            return json.dumps({"error": "Message cannot be empty", "suggestions": []})

        # Get best match
        best_match = self.router.route(message)

        # Get top-k matches
        top_matches = self.router.route_top_k(message, min(top_k, 5))

        # Build response
        result = {
            "primary_skill": best_match.skill,
            "confidence": best_match.confidence,
            "reason": best_match.reason,
            "suggestions": [
                {
                    "skill": m.skill,
                    "confidence": m.confidence,
                    "reason": m.reason,
                }
                for m in top_matches
            ],
        }

        # Add availability info for primary skill
        if best_match.skill:
            skill = self.loader.get_skill(best_match.skill)
            if skill:
                result["available"] = skill.available
                result["skill_description"] = skill.description

                # Add installation hints if not available
                if not skill.available:
                    hints = self.loader.get_install_hints(skill)
                    if hints:
                        result["installation_hints"] = hints

        return json.dumps(result, ensure_ascii=False, indent=2)


class InternalSkillRouter:
    """Internal router with route_top_k method."""

    def __init__(self, loader: SkillLoader):
        self.loader = loader
        self._skills = None

    @property
    def skills(self):
        if self._skills is None:
            self._skills = self.loader.load_all()
        return self._skills

    def route(self, message: str) -> SkillMatch:
        """Route to best matching skill."""
        message_lower = message.lower()

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

        best_skill = max(scores.items(), key=lambda x: x[1])[0]
        best_score = scores[best_skill]
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

    def route_top_k(self, message: str, k: int = 3) -> list[SkillMatch]:
        """Return top-k best matching skills."""
        message_lower = message.lower()

        scores: dict[str, float] = {}

        for name, skill in self.skills.items():
            score = sum(1.0 for keyword in skill.keywords if keyword.lower() in message_lower)
            if score > 0:
                scores[name] = score

        if not scores:
            return []

        # Sort by score descending
        sorted_skills = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [
            SkillMatch(
                skill=name,
                confidence=min(score / 3.0, 1.0),
                reason=f"Matched {int(score)} keywords",
            )
            for name, score in sorted_skills[:k]
        ]


class SkillReadTool(Tool):
    """
    Tool to read a skill's full content.

    After the LLM decides which skill to use (via skill_router),
    it can read the full skill content to get detailed instructions.
    """

    def __init__(self, skill_loader: SkillLoader):
        self.loader = skill_loader

    @property
    def name(self) -> str:
        return "skill_read"

    @property
    def description(self) -> str:
        return """Read the full content of a specific skill's SKILL.md file.
        
Use this AFTER skill_router to get the detailed instructions for a skill.
Returns the skill's markdown content with usage examples, tips, and patterns.
Only read skills that are marked as available - if not available, 
check installation_hints from skill_router response."""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name of the skill to read (e.g., 'github', 'coding-agent')",
                },
            },
            "required": ["skill_name"],
        }

    async def execute(self, skill_name: str) -> str:
        """Execute skill read."""
        if not skill_name or not skill_name.strip():
            return json.dumps({"error": "Skill name cannot be empty", "content": None})

        # Try exact match first
        content = self.loader.get_skill_content(skill_name)

        if not content:
            # Try case-insensitive search
            for name, skill in self.loader.load_all().items():
                if name.lower() == skill_name.lower():
                    content = skill.content
                    skill_name = name
                    break

        if not content:
            # List available skills
            available = list(self.loader.load_all().keys())
            return json.dumps(
                {
                    "error": f"Skill '{skill_name}' not found",
                    "available_skills": available[:10],
                    "content": None,
                }
            )

        # Get skill metadata
        skill = self.loader.get_skill(skill_name)

        result = {
            "skill": skill_name,
            "content": content,
            "available": skill.available if skill else False,
        }

        if skill and not skill.available:
            hints = self.loader.get_install_hints(skill)
            if hints:
                result["installation_hints"] = hints

        return json.dumps(result, ensure_ascii=False, indent=2)
