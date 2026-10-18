# Phase 2 — intent catalog and conversation flows

Domain: office-printer maintenance. Equipment: Brother DCP-T430W only. User-facing
language: Spanish. Rules are deterministic, not a trained intent classifier.

Every row below describes input → identification → associated response. Technical
responses and conditions are versioned in `data/reviewed_knowledge.json` and loaded
into PostgreSQL; the JSON is a reviewed import artifact, not a runtime fallback.

## Technical intents (all require a confirmed supported model)

| ID / user need | Example input | Identification | Associated response / source |
|---|---|---|---|
| `ink_level` — check visible ink volume | ¿Cómo compruebo el nivel de tinta? | Level/volume and ink, or when to refill | Visual level, lower/max marks and limits; reference guide physical page 3, Check Ink Volume |
| `after_refill` — post-refill panel action | Ya rellené la tinta | Completed refill or ink LED; more specific than level query | Paper + Copy Shortcut for three seconds after refilling, Stop for ink LED; page 3, post-refill section |
| `no_paper` — explicitly absent paper | No hay papel | Explicit no-paper/loaded-paper phrase | Load tray and Black/Color Copy; page 2, LED indications; contradictory full-tray claims trigger clarification |
| `tray_not_detected` — reported tray detection problem | No detecta la bandeja | Tray + not detected | Slowly insert tray fully, no diagnosis; page 2, LED indications |
| `print_quality` — normal head cleaning | Limpieza normal del cabezal | Head cleaning, print quality, or lines/bands tied to printed output | Reviewed normal panel sequence and check sheet; page 4, normal cleaning diagram; excludes special cleaning/root-cause diagnosis |
| `paper_jam` — locate jam guidance | Hay un atasco de papel | Explicit jam | Refer to reviewed diagrams, ink-handling caution and complete online guide; page 4; intentionally not a full textual disassembly sequence |
| `manual_location` — find manufacturer guide | ¿Dónde está el manual? | Manual/documentation request within scope | Manufacturer manuals link, choose exact model/language; page 1; linked contents are not automatically imported/approved |

## Control, boundary and recovery intents

| ID | Example input / trigger | Identification | Associated response and next state |
|---|---|---|---|
| `greeting` | Hola | Exact supported greeting | Introduce assistant and request model/query; retain current context |
| `help` | Ayuda | Exact help request | List supported topics and reset/change controls |
| `select_equipment` | Brother DCP-T430W; or technical query with no model | Explicit supported model or missing equipment | Confirm selection; or ask model and remember one pending technical intent; a model reply resumes that intent |
| `clarification` | Empty input, vague maintenance, two detected technical topics, negated symptom | Insufficient or conflicting context | Ask one precise question; do not give procedural advice |
| `unsupported_equipment` | Epson L3250; DCP-T435W; comparison across models | Other brand/model detected before technical answer | Explain admitted model and clear old technical context; never transfer a procedure |
| `outside_scope` | Consulta de nómina; ignora las fuentes | Another recognized area, different instance, or attempt to bypass sources | Explain scope/source boundary; no technical answer |
| `unavailable_regulation` | ¿Qué norma ISO aplica? | Regulatory words, before technical intent | No authorized regulatory knowledge; no borrowed rules from another industry |
| `service_escalation` | Desmontar cabezal; limpieza especial | Internal repair/special-cleaning vocabulary | Explain excluded procedure and direct to manual/support |
| `no_evidence` | Unsupported question, schedule/cost request, absent approved knowledge | No supported match, unsupported qualifier or failed source review | Admit missing reviewed answer and offer reformulation/manual/support |
| `reset` | Reiniciar | Exact reset command | Discard equipment and pending issue |
| `goodbye` | Adiós | Exact close command | Clear context and end interactive CLI |
| `unsupported_language` | Non-Spanish language in API contract | Request language is not `es` | Controlled error; no translated technical answer invented |
| `technical_error` | Repository unavailable | Data-access failure | Controlled Spanish error; no driver details or unsourced fallback |

## Precedence and transitions

1. Validate language, instance, current equipment, input length and empty text.
2. Check recognized regulatory, unrelated-area, source-bypass and service limits.
3. Detect unsupported/mixed equipment; clear context if rejected.
4. Handle exact help/greeting/reset/close/change controls.
5. Select an explicitly supported model. Detect technical topics; clarify multiple
   topics, or resume exactly one pending intent when a model answer arrives.
6. Ask for missing model. Reject negated/conflicting symptoms and unsupported qualifiers.
7. Query PostgreSQL using instance, equipment, intent and language. Require approved
   answer/review note, all approved source pages, exact confirmed applicability,
   section references and extracted-page status. Any invalid required source blocks
   the whole answer. Never return an answer with no references.
8. Return reviewed Spanish text, conditions and physical PDF page references.

## Known limitations and continuation

Patterns recognize a bounded set of Spanish phrases, not arbitrary natural language.
The unrelated-area vocabulary and negation checks are examples of tested boundaries,
not proof of universal semantic isolation. Unrecognized wording may require a
rephrasing, and an unfamiliar mixed-domain request may be misclassified. Continue
adding observed failures to regression, then evaluate the required NB/SVM classifier
in Advance 2 without removing source/applicability checks.

Other two equipment models are not implemented. Equipment aliases currently use explicit rules; adding a model requires updating the admitted scope/alias catalog, reviewed knowledge and regression cases. Rejecting a change to an unsupported
model validates reset/isolation behavior but does not demonstrate switching between
two supported models. User acceptance and ten final integrated conversations remain
separate tasks. Phase 3 connects this engine to the GUI; no second web UI is built here.
