# TechnicalNexus

Equipment-scoped technical assistance grounded in authorized documents.
Development and documentation are in English; the initial GUI is in Spanish.

## Guided consultation and free text

Select the printer, then a topic and specific question, and click **Consultar
orientación**. Topics depend on the model: ink, paper/tray, print quality, documentation, toner and scanner cleaning.
Only questions with currently approved answers and valid sources for the selected
equipment are offered. Each choice sends a canonical Spanish query through the
same NLTK/rules service as the chat; the service checks authorization again.
Options contain no duplicate answer text. Guidance is not a diagnosis or proof of
repair. Free text remains available, including clarification and scope rejection.
Reset clears the conversation, equipment and guided selections.

## Current milestone — Advance 1 review package

Phase 3 integrates the **rules-based maintenance engine into a Spanish Streamlit chat**.
The same engine remains available through the CLI; it is not duplicated in the GUI. Three models are integrated: Brother DCP-T430W (7 reviewed answers), Brother DCP-T220 (8), and Canon imageRUNNER ADVANCE DX C3935i (4). Each answer includes exact source pages and conditions. Unknown regulations, unsupported equipment, unreviewed procedures and
missing knowledge produce explicit limits or clarification.

Phases 1–3 are owner-validated for the implemented Brother scope. Phase 4 has a prepared validation/review package; owner package acceptance and manual validation of the expanded three-model scope remain pending. No LLM,
RAG, embeddings, trained intent/image model, Flask or public deployment exists yet.

## Prerequisites

- Windows development environment; Python **3.12.14** and uv **0.13.1** were validated.
- PostgreSQL **18.3** binaries. The helper defaults to `C:/Program Files/PostgreSQL/18/bin`.
- Port `55432` available for this project's isolated, loopback-only cluster.
- Original PDFs in the three model folders under `ManualesDeImpresoras/`; see `data/document_manifest.json` for exact project-relative paths.
  These are local inputs excluded from Git until redistribution rights are reviewed.

Do not use Python 3.14 for this locked environment. An existing Python 3.12 can
bootstrap uv with `python -m pip install uv==0.13.1`. uv can obtain the pinned
Python if it is not already available. Dependencies are resolved in `uv.lock`;
`pyproject.toml` declares direct requirements. Do not maintain a second lock manually.

## Quick start (PowerShell, from the repository root)

```powershell
uv sync --frozen --link-mode=copy
.\.venv\Scripts\python.exe scripts/local_postgres.py start
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m technicalnexus.cli import-manuals
.\.venv\Scripts\python.exe -m technicalnexus.cli seed-knowledge
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Open `http://localhost:8501`. The first startup helper creates an ignored `.env`
with random local credentials and creates separate development and test databases.
It does not modify an existing PostgreSQL service. It refuses to overwrite an
existing `.env` when initializing a new cluster. Use `POSTGRES_BIN` to select another
PostgreSQL 18 installation. The helper uses short Windows paths where available
to handle accented workspace directory names. If startup fails, inspect the
ignored `work/postgres.log`; do not initialize over an existing cluster.

If no manuals are available, omit seed-knowledge and replace the import command with
`python -m technicalnexus.cli seed`; the GUI can show an empty catalog.

For an existing server or another OS, create dedicated development and test
databases, copy `.env.example` to `.env` and set their URLs. Then run migrations,
seed/import and Streamlit. The helper is Windows-specific; the Python application
and schema do not require Windows. Linux and production portability are unverified.

Local data is under `work/postgres-data`; do not synchronize/copy this live database
as a backup. Stop it before moving the workspace. Originals and generated data
are not uploaded to the private repository automatically.

## Use the web chat

1. Open `http://localhost:8501` and type a question, or select one of the three printers first.
2. If the model is missing, answer in the chat or use the selector. A pending question
   resumes after a valid selection. Source file, physical PDF page and section appear
   under each technical answer.
3. Use **Reiniciar conversación** (or type `reiniciar`) to clear history and equipment.
   Choosing the placeholder in the selector starts a new technical context and clears
   previous messages. Unsupported models typed into chat also clear the technical
   context and synchronize the selector; historical replies remain visible as history.
4. Open the source catalog expander when needed. A successful catalog query displays
   the green PostgreSQL indicator. A connection error is explained without credentials
   or driver traces; the history/context remain available so a later query can retry.

Changing between supported models starts a new case, clears prior history and navigation, and rechecks the new model's source gates. The source catalog is filtered by the selected equipment. Each browser session has separate in-memory state, not
shared global context. History is not stored in PostgreSQL and may disappear when
its WebSocket session ends or the app restarts. Normal Streamlit reruns retain it.
Browser sessions are not authentication or production multi-tenant isolation.

## Useful operations

```powershell
.\.venv\Scripts\python.exe -m technicalnexus.cli health
.\.venv\Scripts\python.exe -m technicalnexus.cli catalog
.\.venv\Scripts\python.exe scripts/local_postgres.py status
.\.venv\Scripts\python.exe scripts/local_postgres.py stop
```

Repeated PDF import is keyed by original SHA-256; it does not duplicate pages or
overwrite reviewed records. Changed PDF bytes create another document identity.
Changing proposed metadata for an existing hash requires an explicit reviewed
update, not a silent import overwrite. A manifest `reviewed_document_type` applies
an explicit reviewed type correction during import without approving pages
or equipment applicability. Individual source download
URLs were not supplied for the original T430W collection; the newer T220/Canon acquisitions include official URLs and checksums. Shared identical documents are stored once and linked to each equipment with separate applicability gates.

## Try the phase-2 engine

```powershell
.\.venv\Scripts\python.exe -m technicalnexus.cli chat
```

Try `Nivel de tinta`, then `Brother DCP-T430W`. The engine asks for the model
and resumes the pending topic with a physical page citation. Other examples:
`Ya rellené la tinta`, `Limpieza normal del cabezal`, `No hay papel`,
`¿Qué norma ISO aplica?`, `cambiar impresora`, `reiniciar`, `adiós`.

Single query with explicit model:

```powershell
.\.venv\Scripts\python.exe -m technicalnexus.cli ask --equipment brother_dcp_t430w --text "¿Cómo compruebo el nivel de tinta?"
```

Run `python scripts/demo_engine.py` using the project environment to reproduce five
real PostgreSQL-backed conversations in `docs/phase2-demo.json`. These are not ten
final GUI conversations or user acceptance. The full [intent/flow catalog](docs/intents-and-flows.md)
describes the supported input patterns and response limits.

Knowledge setup is explicit: apply migrations, import the exact PDFs, then seed the
reviewed manifest. It verifies original hashes, page anchors and applicability, and
upserts 19 scoped answers across three model manifests (`data/reviewed_knowledge.json` and `data/knowledge/*.json`). Other pages remain unapproved. Review notes
identify agent source review and the acceptance status at preparation time; owner CLI acceptance is now recorded in docs/phase2-owner-validation.md. They do not claim
manufacturer certification or approval of every paragraph on a referenced page.

## Tests — one command

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The full suite requires the project PostgreSQL server and `TEST_DATABASE_URL`.
Tests reject a database without a `_test` suffix or one matching development.
Each integration test migrates a unique schema and removes only that schema.
Unit and scope regression tests do not use the development database. UI tests use
Streamlit AppTest. Free-text rules now have unit/regression coverage. This validates tested phrases,
not universal semantic isolation. The real-source GUI evaluation is described below.

For a fresh environment verification, create another environment using the same
lock (`UV_PROJECT_ENVIRONMENT=work/repro-venv` with `uv sync --frozen --link-mode=copy`) and run its
Python against the same test command. Environment-specific secrets stay in `.env`.
If automatic Python installation fails, supply the full path to an existing
Python 3.12.14 using `uv sync --frozen --link-mode=copy --python <path>`.

## Advance 1 validation package

- [Review route and rubric mapping](docs/advance1-review-package.md)
- [38 conversations with actual responses](docs/advance1-validation.md)
- [Machine-readable results](docs/advance1-conversations.json)
- [Current architecture](docs/architecture/current.svg) and [editable Mermaid](docs/architecture/current.mmd)
- [Limitations and continuation](docs/improvement-plan.md)

Reproduce the GUI conversation evidence after normal setup:

```powershell
.\.venv\Scripts\python.exe scripts/validate_advance1.py
```

The script requires the exact local PDF originals and a separate `_test` database.
It creates/migrates a unique schema, imports real sources, seeds the 19 reviewed
answers and executes 38 independent AppTest conversations. It records expected vs
actual outputs and removes only its own schema afterward. It does not modify the
running development database. All predefined checks passed in the recorded run;
this is functional acceptance evidence, not arbitrary-language accuracy or a
physical printer trial. The cases include supported-model switches and explicit checks for different jam and refill instructions.

## Structure

| Path | Responsibility |
|---|---|
| `app.py` | Spanish Streamlit chat, selector, reset and source catalog |
| `src/technicalnexus/` | Configuration, conversation adapter/service, rules engine, scope, PDF extraction and reviewed knowledge repository |
| `migrations/` | Immutable Alembic schema revisions |
| `data/document_manifest.json` | Proposed titles, editions and applicability notes |
| `tests/` | Unit, selection regression, PostgreSQL integration and UI checks |
| `avance1roadmap.md` | Active English plan and milestone status |
| `NotaAcademica.md` | Living academic draft, source material for the final report |
| `docs/` | Source inventory, test evidence and user acceptance checklist |

## Storage and future integration

PostgreSQL stores catalog, page text, applicability and reviewed-answer relationships.
PDFs, images and model weights remain external, referenced by stable IDs/paths/hashes.
The local bootstrap account is a development owner, not a production application
role. Production needs a restricted role, hosted persistent PostgreSQL, backup
policy and a continuously available Flask host.

pgvector is not available in the current PostgreSQL installation and is not needed
for the current rules-based version. Future embeddings can reference existing pages/fragments with model,
version and dimension metadata; no SQLite-to-PostgreSQL migration is planned.
RAG remains optional. Required later: TF-IDF/BoW + NB/SVM, ResNet50/EfficientNet,
agent coordination and Flask. Streamlit Community Cloud will host the GUI and
Cloudflare Tunnel will expose the later Flask service; a tunnel is not hosting.

Repository: https://github.com/Praxisinfinitum/TechnicalNexus (private).
See [the review package](docs/advance1-review-package.md) and `docs/user-validation.md` for the three phase-4 owner checks.

## Added models — 2026-10-22

See [the model-expansion review](docs/model-expansion.md) for the exact answer
scope and source review. Canon toner and glass-cleaning options do not expose
Brother ink/head-cleaning answers. The Canon European Spanish PDF is used for
stable physical-page references; the three enabled maintenance sections were
cross-checked against the official Latin America manual. Other regional details,
regulations and accessories are not authorized by that review.

Import is repeatable and uses explicit `relative_path` entries for new folders.
`MANUALS_PATH` remains a compatibility override for the original T430W entries.
All original PDFs remain local, including Canon's personal/non-commercial licensed
manual; the private repository contains metadata and paraphrased reviewed answers.
