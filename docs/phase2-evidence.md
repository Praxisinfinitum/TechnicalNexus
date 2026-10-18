# Phase 2 — implementation and validation

Status: implemented for Brother DCP-T430W; owner checks pending; models 2/3 deferred.
This is development phase 2 of Advance 1, **not the course's Advance 2**.

## Implemented behavior

- NLTK RegexpTokenizer provides real deterministic tokenization; normalization
  preserves negation and requires no external corpus download.
- Explicit query/context and status/intent/text/reference contract. Session state
  belongs to the caller; one engine instance can serve independent contexts.
- Seven Spanish technical/navigation answers reviewed against the local reference
  guide, including its diagrams, with exact SHA-256 and physical page/section.
- Agent source review is recorded separately from pending owner acceptance. It is
  not manufacturer certification, a mechanical repair test or blanket approval
  of all content on the reviewed PDF pages.
- PostgreSQL repository enforces instance/equipment/intent/language, approved answer,
  nonempty review note, confirmed applicability and every required approved page.
- Alembic `0002`: review conditions/note, section references and unique answer scope.
- Repeatable review-manifest import verifies original bytes and page anchors.
  It does not authorize other manuals or models and never falls back to JSON at runtime.
- CLI `chat` and `ask`; source citations and controlled database errors.
- Five actual multi-turn PostgreSQL-backed demonstrations saved to `phase2-demo.json`.
  These are agent-executed CLI evidence, not owner approval or the complete phase-4
  ten-conversation GUI requirement.

## Checks and observed corrections

- First expanded regression found that a broad normative pattern matched “normal”.
  Changed to explicit norma/normas/normativa patterns; normal cleaning now works.
- Restricted quality patterns to printing/head-cleaning context; unrelated quality
  requests no longer match by the word alone. Full-tray/no-paper contradictions
  ask for clarification.
- Unit tests cover NLTK normalization, missing-model resumption, unsupported-model
  context reset, independent contexts and missing/failing knowledge repository.
- Regression covers recognized topics, norms/HR, other brands/models, mixed models,
  source-bypass requests, internal/special procedures, negation, ambiguity, reset
  and closure. These cases do not establish universal language understanding.
- Real PostgreSQL integration checks migration, repeatable imports, all review flags,
  rejection when any secondary source is invalid, exact scope/language, idempotent
  knowledge seeding and changed-original detection.

## Final executed results

- Full accumulated suite: **58 passed in 7.54 s**, including phase-1 regressions,
  PostgreSQL migration/source gates and Spanish catalog smoke tests.
- PostgreSQL health: version 18.3, connection verified; pgvector still unavailable
  and unused.
- Reviewed seeding repeated successfully with the same seven answer scopes, without
  duplicate answers or references. Exact original PDF checksums and page anchors
  were verified again.
- Interactive boundary demonstrated using single-query CLI for normal head cleaning;
  Spanish response included conditions and reference-guide physical page 4.
- Five actual multi-turn scenarios recorded after engine integration. These cover all
  seven technical/navigation responses plus missing-model recovery, limits and reset.

## Pending acceptance and next work

Use the three checks in `user-validation.md`. GUI conversation integration is phase 3;
the current web page remains a catalog/status page. Other models and corresponding
sources must be provided before declaring the three-model advance complete. Unknown
phrasing and unsupported procedures require further dataset/regression work; no
trained-intent accuracy, CNN result or measured user time saving exists yet.
