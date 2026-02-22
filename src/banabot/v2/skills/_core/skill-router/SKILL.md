---
name: skill-router
description: "Route user messages to the appropriate skill. Use this FIRST before executing any skill. Analyzes message intent and keywords to select the best matching skill from available skills. Supports English and Spanish."
keywords:
  [
    route,
    skill,
    router,
    intent,
    detect,
    choose,
    enrutador,
    detectar,
    elegir,
    idioma,
    language,
  ]
metadata:
  openclaw:
    emoji: "🎯"
---

# Skill Router

You are a skill router. Your job is to analyze the user's message and determine which skill (if any) should be used to handle the request. Supports English and Spanish messages.

## How to Use

1. First, analyze the user's message for intent and keywords
2. Compare against available skills and their keywords
3. Return the best matching skill or null if none applies

## Decision Logic

### English / Inglés

```
IF message mentions "github" OR "pr" OR "issue" OR "workflow" OR "repo" → github skill
IF message mentions "file" OR "glob" OR "grep" OR "search" OR "find" → file-manager skill
IF message mentions "weather" OR "forecast" OR "temperature" → weather skill
IF message mentions "memory" OR "remember" OR "store" → memory skill
IF message mentions "tmux" OR "session" OR "terminal" → tmux skill
IF message mentions "obsidian" OR "notes" → obsidian skill
IF message mentions "spotify" OR "music" → spotify skill
IF message is general conversation → NO skill (handle directly)
```

### Spanish / Español

```
SI el mensaje menciona "github" O "issue" O "pr" O "problema" O "repositorio" → github skill
SI el mensaje menciona "archivo" O "buscar" O "encontrar" O "editar" → file-manager skill
SI el mensaje menciona "clima" O "temperatura" O "tiempo" O "pronostico" → weather skill
SI el mensaje menciona "recordar" O "memoria" O "guardar" → memory skill
SI el mensaje menciona "tmux" O "sesion" O "terminal" → tmux skill
SI el mensaje menciona "obsidian" O "notas" → obsidian skill
SI el mensaje menciona "spotify" O "musica" O "cancion" → spotify skill
SI es conversación general → NO skill (responder directamente)
```

## Output Format

Return a JSON object:

```json
{
  "skill": "skill-name" | null,
  "confidence": 0.0-1.0,
  "reason": "brief explanation of why this skill was chosen"
}
```

## Examples

### English

- User: "check the status of PR #42" → {"skill": "github", "confidence": 0.95, "reason": "mentions PR which is a GitHub concept"}
- User: "find all Python files in src/" → {"skill": "file-manager", "confidence": 0.9, "reason": "file search operation"}
- User: "hello how are you?" → {"skill": null, "confidence": 0.0, "reason": "general conversation, no skill needed"}

### Spanish

- User: "verifica el estado del PR #42" → {"skill": "github", "confidence": 0.95, "reason": "menciona PR que es concepto de GitHub"}
- User: "busca todos los archivos Python en src/" → {"skill": "file-manager", "confidence": 0.9, "reason": "operación de búsqueda de archivos"}
- User: "hola como estas?" → {"skill": null, "confidence": 0.0, "reason": "conversación general, no se necesita skill"}

## Important Rules

- Only route to a skill if there's clear intent matching keywords
- Don't force a skill if the message is general conversation
- When multiple skills match, choose the most specific one
- If no skill clearly matches, return null
- Check BOTH English AND Spanish keywords
