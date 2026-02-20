# 🍌 Banabot Roadmap

## Conectividad

- [ ] **Conectar Email** — Revisar configuración SMTP/IMAP

---

## Smart — Personalidad e Inteligencia

- [ ] **Onboarding conversacional** — Al iniciar el agente por primera vez, no conoce al usuario. Necesita una platica inicial para:
  - [ ] Llenar SOUL.md (personalidad del bot)
  - [ ] Llenar USER.md (conocer al usuario)
  - [ ] Hacer preguntas naturales sobre preferencias, nombre, cómo quiere que le llame, etc.
- [ ] **Detección de primera vez** — El agente debe saber que "acaba de nacer" y no tiene contexto del usuario
- [ ] **Persistencia de personalidad** — Que el bot se sienta único y conocido

---

## Memoria y Contexto

### Configuración de Modelo ✅ COMPLETADO
- [x] **Tabla de modelos** — Crear tabla con tokens máximos, mínimos y recomendados por modelo:
  - GPT-4o: ~128K tokens → 50K max_tokens
  - GPT-4o-mini: ~128K tokens → 50K max_tokens
  - Claude Opus 4.5: ~200K tokens → 80K max_tokens
  - Claude Sonnet 4.5: ~200K tokens → 80K max_tokens
  - DeepSeek Chat: ~64K tokens → 25K max_tokens
  - Gemini 2.5 Pro: ~1M tokens → 100K max_tokens
- [x] **Ajustar max_tokens dinámicamente** — Según el modelo seleccionado, configurar valores óptimos
- [x] **Configuración de temperatura** — Agregar al wizard con valores recomendados por tipo de uso

### Memoria a Medio Plazo
- [ ] **Resúmenes de conversaciones** — Guardar resúmenes temporales (1 mes)
- [ ] **Mini-RAG para eventos** — Conocer eventos recientes del usuario (ej: "te acuerdas que hace 2 semanas dijiste que tu tía se va a casar")
- [ ] **Memoria episódica** — Guardar eventos importantes sin ser "largo plazo" pero sí conocer "acontecimientos"

### Compresión de Memoria
- [ ] **agent/loop.py:407-491** — Revisar compresión de mensajes cuando superan 50 mensajes
- [ ] **Mecanismo de recuperación** — Evaluar forma de recuperar detalles importantes sin perder ligereza
- [ ] **Compresión con pérdida** — Detalles importantes pueden desaparecer para siempre

### Búsqueda en Memoria
- [ ] **Búsqueda semántica** — Agregar embeddings para búsqueda vectorial
- [ ] **Índices** — Implementar índices para búsquedas rápidas
- [ ] **Limpieza automática** — HISTORY.md y sesiones JSONL crecen sin límite

---

## Infraestructura

- [ ] **Eficiencia de RAM** — Evaluar cómo hacer todo sin comer mucha RAM
- [ ] **Limpieza de archivos** — Auto-limpieza de archivos temporales y logs antiguos
- [ ] **Caché inteligente** — Implementar caché para respuestas frecuentes

---

## Herramientas (Tools)

### Retry y Fallback
- [ ] **agent/tools/registry.py:61-62** — Si un tool falla, el agente debe reintentar o buscar estrategia alternativa
- [ ] **Retry automático** — Implementar reintentos con backoff exponencial
- [ ] **Fallback de tools** — Si un tool no funciona, intentar alternativa

### Concurrencia
- [ ] **Ejecución paralela** — Los tools I/O-heavy (web fetches) ejecutarse en paralelo
- [ ] **Batch de tools** — Procesar múltiples tools simultáneamente

---

## Prioridades Sugeridas

1. **ALTA** — Memoria y Contexto (configuración de modelo + tabla de tokens)
2. **ALTA** — Onboarding conversacional (primera experiencia del usuario)
3. **MEDIA** — Retry en tools
4. **MEDIA** — Búsqueda semántica en memoria
5. **BAJA** — Concurrencia en tools

---

## Notas

- Mantener siempre la filosofía de "ligero" (banabot no debe ser pesado)
- Priorizar features que mejoren la experiencia sin aumentar complejidad
- Evaluar costo-beneficio de cada feature (memoria, RAM, API calls)
