# Casos de Evaluación - BanaBot

## Formato
Cada caso es: **"Usuario dice X" → "Bot debería hacer Y"**

---

## CASO 1: Transparencia

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 1.1 | "¿Qué clima hace?" | Usar weather tool (no web_search) |
| 1.2 | "¿Usaste alguna herramienta?" | **NUNCA** decir "no usé herramientas" si usó alguna |
| 1.3 | (después de buscar) "¿Qué tools usaste?" | Decir explícitamente cuál/es usó |

---

## CASO 2: Guardar Preferencias

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 2.1 | "Tengo un perro" | Guardar en profile: `key=pet` |
| 2.2 | "Vivo en Puebla" | Guardar en profile: `key=location` |
| 2.3 | "Me gusta el fútbol" | Guardar en profile: `key=interests` |
| 2.4 | "Soy alergic@ a los gatos" | Guardar en profile: `key=allergies` |
| 2.5 | "Trabajo en TechCorp" | Guardar en profile: `key=work` |

---

## CASO 3: Memoria

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 3.1 | "Mi perro se llama Gordo" | Escribir en MEMORY.md |
| 3.2 | "/new" (nueva sesión) | Recordar "Gordo" en sesión siguiente |
| 3.3 | (después de 3+ intercambios) | Escribir en HISTORY.md |

---

## CASO 4: Ubicación

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 4.1 | "¿Qué clima hace?" (sin location) | **NO** asumir Nueva York |
| 4.2 | "Estoy en Ciudad de México" | Guardar location, usar para clima |
| 4.3 | "Busca sushi" | Buscar en su ciudad (no genérico) |

---

## CASO 5: Clima

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 5.1 | "¿Cómo está el clima?" | Usar **weather** tool |
| 5.2 | "¿Va a llover?" | Responder sí/no con probabilidad |
| 5.3 | "¿Qué temperatura tiene?" | Dar temperatura específica |

---

## CASO 6: Onboarding

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 6.1 | (primera vez) "Hola" | Responder con wonder/confusión |
| 6.2 | - | Preguntar cómo llamarse |
| 6.3 | "Llámame Julio" | Guardar `bot_name=Julio` |
| 6.4 | "Me llamo Álvaro" | Guardar `user_fields.name=Álvaro` |
| 6.5 | (ya tiene nombres) | `needs_onboarding=false` |

---

## CASO 7: Recordatorios

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 7.1 | "Recuérdame en 1 hora que tengo junta" | Crear cron, confirmar hora |
| 7.2 | "Recuérdame darle de comer al perro" | Guardar **contexto** "perro" en el cron |

---

## CASO 8: Estilo

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 8.1 | "Usa emojis" | Responder con emojis |
| 8.2 | "Sé más formal" | Cambiar tono a formal |
| 8.3 | "Sé breve" | Responder en pocas palabras |

---

## CASO 9: Búsquedas

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 9.1 | "¿A qué hora juegan las Chivas?" | Incluir año actual (2026) en búsqueda |
| 9.2 | "¿Cuánto quedó el América?" | Buscar resultado específico, no genérico |
| 9.3 | "Comida china cerca" | Usar su location en búsqueda |

---

## CASO 10: Configuración

| # | Usuario dice | Bot debería hacer |
|---|-------------|-------------------|
| 10.1 | "Quiero usar Brave Search" | Configurar Brave como provider |
| 10.2 | "Cambia a GPT-4" | Cambiar modelo en config |

---

*Casos de evaluación - formato simple*
