# Phase 3 — Spanish web chat integration

Status: implemented for Brother DCP-T430W, owner validation accepted. No additional
model has been invented or added. This is phase 3 of Advance 1 development, not
the course's Advance 2 or the final deployed product.

## Implemented behavior

- Streamlit chat calls the existing phase-2 rules engine through `application.py`.
  No inference rules were copied into the presentation layer.
- `chat.py` owns immutable presentation state and messages; Streamlit stores one
  state per session. No global equipment/history or shared SQLAlchemy Session.
- Equipment selector and typed model changes remain synchronized. A model selected
  in response to a pending question resumes that question, with source references.
- The reset button and typed reset both remove old conversation history and model.
  Selecting the placeholder starts a fresh technical context. An unsupported model
  typed into chat clears active model/pending state while retaining the conversation
  as history, including the rejection explanation.
- Technical replies show original filename, physical page and reviewed section.
  The catalog is available in a collapsed expander; approved answers remain distinct
  from catalogued documents. No original manual download was added to the website.
- Data errors use Spanish messages without driver traces or credentials. Context
  and history survive a failed query; a subsequent request can retry after recovery.
- Each operation closes its database session/engine. Chat histories are not stored
  in PostgreSQL, and browser refresh/restart may end a Streamlit session.

## Automated validation

Final complete suite: **66 passed in 21.00 s**, on the pinned Python environment
and PostgreSQL 18.3. All prior engine, source approval, import, migration and scope
regression tests remain included. No dependency or lockfile change was needed.

- Unit checks: immutable history updates, selector/reset behavior, pending-question
  resumption and typed reset clearing old content.
- AppTest: missing model → selector answer → referenced response; regular rerun
  without duplicate messages; reset; typed model/selector synchronization; unsupported
  model rejection; two independent sessions; controlled connection failure and retry.
- GUI checks use synthetic reviewed knowledge inside a unique schema in the dedicated
  PostgreSQL test database. They do not require private PDF originals or mutate the
  development knowledge. Failure/recovery stays inside that same test schema.
- No need for the owner to stop PostgreSQL to test errors manually.

## Browser verification

Agent executed a real browser interaction against the development app:

1. Sent `Nivel de tinta` with no selected model and observed the model question.
2. Selected Brother DCP-T430W in the GUI.
3. Observed the resumed Spanish answer, conditions and reference-guide physical page 3.

Evidence: [referenced web conversation](screenshots/phase3-referenced-chat.png).
This is agent browser evidence, not owner validation or a completed ten-conversation
final assessment.

## Owner checks and limitations

The three short owner checks are in `user-validation.md`; their results remain
pending. The initial interface supports one equipment model, so changing between
two supported printers cannot be demonstrated yet. Session separation is not
authentication, authorization between users or production multi-tenant isolation.
Rules still recognize bounded wording and can require reformulation. Final ten
conversations, broader analysis and final packaging are phase 4; Flask, visual
classification, agent coordination and cloud deployment remain later coursework.

Owner acceptance: the owner explicitly reported all three phase-3 checks successful. This is reported user validation, distinct from the agent browser interaction above.
