# Intent catalog and conversation flows — three-model scope

Domain: office-printer maintenance. Equipment: Brother DCP-T430W, Brother DCP-T220 and Canon C3935i. User-facing
language: Spanish. Rules are deterministic, not a trained intent classifier.

Every row below describes input → identification → associated response. Technical
responses and conditions are versioned in `data/reviewed_knowledge.json` plus `data/knowledge/*.json` and loaded
into PostgreSQL; the JSON is a reviewed import artifact, not a runtime fallback.

## Current technical-intent matrix

All rows require an exact model. A missing entry means no reviewed answer and no
guided option; it never borrows a response from another printer. Page numbers are
physical PDF pages. The detailed Spanish text/conditions live in review manifests.

| Intent / example | Identification | T430W | T220 | Canon C3935i |
|---|---|---|---|---|
| ink_level / Nivel de tinta | Ink + level/volume | Visible tank level, p. 3 | Own visible level, p. 193 | No evidence |
| after_refill / Ya rellené la tinta | Completed refill/ink LED | Papel + Atajo Copia, p. 3 | Close caps/cover; Detener if LED flashes, p. 196 | No evidence |
| no_paper / No hay papel | Explicit absence of paper | Load + Copia controls, p. 2 | Load + Inicio controls, p. 165 | No evidence |
| tray_not_detected / Bandeja no detectada | Tray + not detected | Slow complete insertion, p. 2 | Own insertion guidance, p. 165 | No evidence |
| print_quality / Limpieza de cabezales | Head cleaning/print-quality pattern | Normal Copia sequence, p. 4 | Normal Inicio sequence, p. 200 | No evidence |
| paper_jam / Atasco de papel | Explicit jam | Diagram referral, p. 4 | Refer full illustrated inside-equipment sequence starting unplugged, p. 170 | Follow display, do not power off or force paper, p. 148 |
| manual_location / Dónde está el manual | Manual/documentation | Official model guide, p. 1 | Own guide, p. 1 | Edition + Latin America link, p. 1 |
| toner_level / Nivel de tóner | Toner + level/remaining | No evidence | No evidence | Monitor estado/Cancelar → Consumibl./Otros, p. 145 |
| glass_cleaning / Limpiar el cristal del escáner | Cleaning + glass/scanner | No evidence | Unplug, soft damp cloth, p. 199 | Stop jobs, power off/unplug, supplied cloth, dry/close/restart, pp. 103–104 |

## Original T430W technical-intent details

The following table describes the original T430W response set only; use the matrix
above for the new models.


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

All three selected models are now implemented with bounded answers. Aliases are
explicit rules; adding another model requires scope/alias changes, source review
and regression cases. Approved-model switches and mixed-model refusals are covered
by current evaluation; owner acceptance of the expansion remains pending.

## Guided route and rule reuse

Equipment selection precedes topic and specific question. guidance.py defines
nine labels/canonical queries across model-filtered topics (ink, paper/tray, print quality, documentation, toner and scanner cleaning). KnowledgeRepository.find filters available choices using the same
approval and source applicability gates as answers. Clicking consultation submits
the canonical text to the existing NLTK/rules service, which rechecks the database.
No answers are embedded in widgets. Invalidated choices disappear on rerun; the
free-text route still supports clarification, unknown models and unavailable
regulations. Reset clears navigation and conversation together. The print-quality
rule accepts both cabezal and cabezales; excluded chemicals remain blocked.
