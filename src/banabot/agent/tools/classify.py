"""Message classifier tool for auto-learning user preferences."""

import re
from typing import Any

from banabot.agent.tools.base import Tool


class ClassifyMessageTool(Tool):
    """
    Classify user messages and extract preferences for auto-learning.

    Supports MULTIPLE LANGUAGES: Spanish, English, French, etc.

    This tool analyzes a user message to determine:
    - interest: User expresses interest in something
    - personal_fact: Personal fact about the user
    - question_with_interest: Question that reveals preference
    - no_relevant: Nothing to save
    """

    @property
    def name(self) -> str:
        return "classify_message"

    @property
    def description(self) -> str:
        return """Classify user message and extract what to remember (MULTI-LANGUAGE).
Analyzes if the message contains:
- interests (me gusta/I like/me gusta/me encanta)
- personal facts (tengo/I have/ich habe)
- questions that reveal preferences
- Returns what to save in profile"""

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The user's message to classify (any language)",
                },
            },
            "required": ["message"],
        }

    async def execute(self, message: str, **kwargs: Any) -> str:
        """Classify the message and return what to save."""
        message_lower = message.lower()

        # === PERSONAL FACTS (MULTI-LANGUAGE) ===
        personal_patterns = [
            # Spanish
            (r"tengo (\d+)", "personal_fact", "has_count", "tengo"),
            (
                r"tengo (un |una |dos |tres |4 )?(gato|perro|pez|pájaro|hamster|loro|conejo|tortuga)",
                "pet",
                "pet",
                "tengo",
            ),
            (r"me llamo", "name", "name", "me llamo"),
            (r"vivo en", "location", "location", "vivo"),
            (r"trabajo en", "work", "work", "trabajo"),
            (r"soy de", "origin", "origin", "soy de"),
            (r"estoy enamorado de", "crush", "romantic", "enamorado"),
            (r"soy alérgico a", "allergies", "allergy", "alérgico"),
            # English
            (r"\bi have (\d+)", "personal_fact", "has_count", "i have"),
            (
                r"\bi have (a |an |two |)?(cat|dog|fish|bird|hamster|rabbit|pet)",
                "pet",
                "pet",
                "i have",
            ),
            (r"\bmy name is", "name", "name", "my name"),
            (r"\bi live in", "location", "location", "i live"),
            (r"\bi work at", "work", "work", "i work"),
            (r"\bi am from", "origin", "origin", "i am from"),
            (r"\bi am in love with", "crush", "romantic", "in love"),
            (r"\bi am allergic to", "allergies", "allergy", "allergic"),
            # French
            (r"j'ai (\d+)", "personal_fact", "has_count", "j'ai"),
            (
                r"j'ai (un |une |deux |)?(chat|chien|poisson|oiseau|hamster|lapin)",
                "pet",
                "pet",
                "j'ai",
            ),
            (r"je m'appelle", "name", "name", "je m'appelle"),
            (r"j'habite à", "location", "location", "j'habite"),
            (r"je travaille chez", "work", "work", "je travaille"),
        ]

        for pattern, field, category, _ in personal_patterns:
            if re.search(pattern, message_lower):
                return f'{{"action": "set_user_field", "key": "{field}", "value": "{message}"}}'

        # === INTERESTS (MULTI-LANGUAGE) ===
        interest_patterns = [
            # Spanish
            (r"me gusta (mucho |)?(.+)", "interests", "me gusta"),
            (r"me encanta (.+)", "interests", "me encanta"),
            (r"me fascina (.+)", "interests", "me fascina"),
            (r"me apasiona (.+)", "interests", "me apasiona"),
            # English
            (r"\bi like (a lot |)?(.+)", "interests", "i like"),
            (r"\bi love (.+)", "interests", "i love"),
            (r"\bi'm interested in (.+)", "interests", "interested"),
            (r"\bi'm really into (.+)", "interests", "really into"),
            # French
            (r"j'aime (.+)", "interests", "j'aime"),
            (r"je suis passionné par (.+)", "interests", "passionné"),
        ]

        for pattern, field, _ in interest_patterns:
            match = re.search(pattern, message_lower)
            if match:
                # Extract the interest (group 1 or 2 depending on pattern)
                value = match.group(1) or match.group(2) or message
                value = value.strip()
                if value:
                    return f'{{"action": "set_user_field", "key": "{field}", "value": "{value}"}}'

        # === SEARCH/QUESTION that reveals interest ===
        search_patterns = [
            # Spanish
            (
                r"busca.*(videos?|películas?|series?|recetas?|juegos?|música|libros?|artículos?)",
                "search_interest",
            ),
            (r"busco.*(videos?|recetas?|información|de cómo)", "search_interest"),
            (r"cuál (me )?(recomiendas|es el mejor)", "recommendation"),
            (r"qué (juego|serie|película|actor|actriz|libro) (me )?", "recommendation"),
            (r"dónde puedo (comprar|encontrar|ver)", "shopping_interest"),
            # English
            (r"find.*(videos?|movies?|shows?|recipes?|games?|music|books?)", "search_interest"),
            (r"search for", "search_interest"),
            (r"what (game|movie|show|book|series) (should i|do you recommend)", "recommendation"),
            (r"which (game|movie|show) (is better|should i)", "recommendation"),
            (r"where can i (buy|find|watch)", "shopping_interest"),
            # French
            (r"trouve.*(vidéos?|films?|séries?|recettes?|jeux?)", "search_interest"),
            (r"quel (jeu|film|série|livre)", "recommendation"),
        ]

        for pattern, field in search_patterns:
            if re.search(pattern, message_lower):
                return f'{{"action": "set_user_field", "key": "{field}", "value": "{message}"}}'

        # === NO RELEVANT INFO ===
        return '{"action": "none"}'
