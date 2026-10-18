# Phase 4 — validation and review package

Status: validation/package implementation ready for Brother DCP-T430W; owner
package checks pending. Two additional models and their validation are deferred.
Phases 1–3 are accepted by the owner. Do not mark the whole three-model advance
complete on the basis of this single-model package.

## Executed checks

- 22 independent Streamlit AppTest conversations, 50 turns: **22/22 and 50/50 passed**
  the predefined checks. Cases were written before execution and include actual
  source-backed replies, ambiguity, missing model, HR, absent norms, unsupported
  device, reset, closure, excluded procedures and DB failure/recovery.
- Full inputs, expected/actual outputs, page references, source hashes, active
  equipment and per-turn checks are in advance1-conversations.json. The readable
  transcript and case table are in advance1-validation.md.
- Built a fresh schema from Alembic 0002, imported the supplied PDF originals and
  seeded reviewed knowledge: 10 documents, 169 pages and 7 approved answers.
  This is real source data, not synthetic-answer fixtures. The validation schema
  was removed after use; development data was not cleaned or modified.
- Rebuilt `work/phase4-venv` from uv.lock using Python 3.12.14 and copy mode:
  **66 accumulated tests passed in 27.05 s**. PostgreSQL 18.3 was used for persistence
  integration. Linux/production and concurrent load were not validated.
- Latest GUI evaluation: 49 normal turns averaged 169.86 ms, range
  96.89–428.95 ms. The simulated unavailable endpoint turn took 9012.88 ms.
  These measurements include UI/framework/database work and are not production
  service-latency or model-accuracy benchmarks.
- The chat adapter now records intent IDs as internal evidence metadata, including
  reset. This does not add a user-visible classifier score or change response rules.

## Package contents

README, living NotaAcademica, root roadmap, architecture SVG/editable Mermaid,
intent flows, reviewed knowledge manifest, source inventory, transcripts and
expected cases, regression suite, validation runner and improvement plan.
See advance1-review-package.md for the criterion-to-evidence map and review route.
Earlier phase-3 browser screenshot remains available as agent browser evidence;
the new 22-conversation report is explicitly AppTest execution.

## Observed limitations and acceptance boundaries

The unavailable-DB response is slow relative to normal test turns; repeated
catalog/answer requests during reruns are a plausible contributor and an improvement
target, without introducing an unsourced fallback. Phrase rules do not establish
universal semantic isolation. Unknown-model rejection does not replace tests across
two supported models. These limitations and corresponding next actions are in
improvement-plan.md and the academic draft.

Owner phase-4 review has not occurred. Instructor access to the private repository
must be arranged before submission. No Canvas submission, public deployment, trained
classifier metric, physical printer repair result or final paginated report/video
is represented as complete.

## Package consistency checks

- Fourteen Markdown files checked: local linked files exist and code fences balance.
- Architecture SVG is well-formed XML; a local raster preview of its shapes/text
  was inspected for legibility. Editable Mermaid and SVG are included.
- Evaluated code/input fingerprint still matches the generated conversation report.
- GitHub CLI verified owner access and PRIVATE visibility for Praxisinfinitum/TechnicalNexus.
  This does not prove instructor access or change sharing permissions.
- Development PostgreSQL remained healthy after the isolated validation run.


## Guided interface refinement validation

Latest run: **77 tests passed in 22.01 seconds** in .venv, including all seven
canonical query mappings, guided/text answer equivalence, navigation reset and
revoked-source filtering. The prior clean-environment 66-test result above is
historical. Regenerated real-source evidence: **22/22 conversations, 50/50 turns**,
including four guided topics and the owner-reported plural cleaning phrase.
Guided turns include selector interactions and are not comparable with isolated
inference latency. Owner acceptance of the new interface remains pending.
