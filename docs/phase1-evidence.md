# Phase 1 — executed evidence

Date: 2026-10-17. Windows x64, Python 3.12.14, uv 0.13.1, PostgreSQL 18.3.
Resolved versions are in `uv.lock`; Streamlit 1.66.0, NLTK 3.10.3, SQLAlchemy 2.1.5,
Alembic 1.20.0, pypdf 6.21.1 and psycopg 3.3.6 were exercised.

## Executed results

- Alembic revision `0001`: applied to the dedicated development database.
- PDF import: 10 documents, 169 physical pages; 165 extracted, 3 empty and 1 flagged
  for replacement characters. Zero approved pages and zero authored technical answers.
- Source preparation: metadata manifest plus original/normalized text per page,
  hashes and pending equipment applicability; originals unchanged.
- Initial full test run: 14 passed. Alembic path-separator warning corrected afterward.
- Clean environment `work/repro-venv` rebuilt from `uv.lock`: **14 passed in 14.41 s**.
  No SQLite used for persistence checks. Unique test schemas are migrated/cleaned
  in a dedicated `_test` database, never the development database.
- Unit checks: configuration restrictions, normalization, proposed classification,
  language fallback and context immutability.
- Regression checks: valid model, unknown equipment and another knowledge instance.
  These test explicit selection, not arbitrary-language intent recognition.
- Integration checks: migration, repeated seed/import, references/page identity,
  unapproved extracted text, instance filtering and unknown-equipment rejection.
- GUI checks: Streamlit AppTest verifies initial Spanish catalog and controlled
  DB error without displaying credentials. The initial app intentionally has no chat.
- Browser inspection: local app opened successfully with the Spanish phase notice,
  Brother selector and confirmed PostgreSQL connection. Left available for owner review.
- Initial reference-guide page rendered locally and visually checked against title,
  model groups, multilingual columns and extraction needs. This is a sample check,
  not visual verification of all 169 pages.
- pgvector availability query: false. It is not a dependency of phase 1; install/
  evaluate it before introducing embeddings later.

## Corrections made during execution

- PostgreSQL was installed outside PATH. Used its existing binaries to create an
  isolated loopback cluster on port 55432, without editing existing services.
- Windows localized paths affected initial startup. Helper now uses short paths
  where available; an independent startup confirmed connection availability.
- Added fontTools and cryptography after real PDF parsing exposed font/AES needs.
- OneDrive rejected hardlink installation in a fresh environment. Copy mode produced
  the reproducible environment; README documents it. Earlier partial environments
  remain ignored under `work/` and are not deliverables.
- Automatic uv Python download did not produce its expected installation path.
  The clean rebuild used the already available exact Python 3.12.14 interpreter.

## Limits and remaining work

Owner validation is pending in `docs/user-validation.md`. Two printer models are
pending selection. Source classification/applicability and answer approval require
phase-2 review. Detailed online user guide and visual dataset are candidates, not
imported/approved additions. No ten-conversation evidence, intent/CNN metrics, RAG,
agent, API, container or public deployment exists at this milestone. Linux and
production environments have not been tested. Markdown diagrams have not yet been
exported into a final paginated academic document.

## Owner feedback follow-up

Catalog and architecture accepted by the owner. Document 6 classification explicitly
reviewed as driver_guide; Spanish label updated to Guía de driver. Import applies
reviewed type metadata without approving technical content. Regression: 14 passed
in 5.41 s. Database health query confirmed PostgreSQL 18.3; Spanish GUI confirmed
by owner, observation of the green DB status message remains pending.
