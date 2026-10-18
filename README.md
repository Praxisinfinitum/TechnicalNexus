# TechnicalNexus

Equipment-scoped technical assistance grounded in authorized documents.
Development and documentation are in English; the initial GUI is in Spanish.

## Current milestone

Phase 1 is a foundation and source catalog, **not a working maintenance chatbot**.
It provides a Streamlit catalog, PostgreSQL schema and migrations, repeatable PDF
import, a language-independent conversation contract, and automated tests.
Only Brother DCP-T430W is selected. Two additional models remain owner decisions.
No extracted paragraph is approved automatically. No LLM, RAG, embeddings,
image model, Flask API or public deployment has been implemented.

## Prerequisites

- Windows development environment; Python **3.12.14** and uv **0.13.1** were validated.
- PostgreSQL **18.3** binaries. The helper defaults to `C:/Program Files/PostgreSQL/18/bin`.
- Port `55432` available for this project's isolated, loopback-only cluster.
- Original PDFs under `ManualesDeImpresoras/DCP-T430W/` for document import.
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
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Open `http://localhost:8501`. The first startup helper creates an ignored `.env`
with random local credentials and creates separate development and test databases.
It does not modify an existing PostgreSQL service. It refuses to overwrite an
existing `.env` when initializing a new cluster. Use `POSTGRES_BIN` to select another
PostgreSQL 18 installation. The helper uses short Windows paths where available
to handle accented workspace directory names. If startup fails, inspect the
ignored `work/postgres.log`; do not initialize over an existing cluster.

If no manuals are available, replace the import command with
`python -m technicalnexus.cli seed`; the GUI can show an empty catalog.

For an existing server or another OS, create dedicated development and test
databases, copy `.env.example` to `.env` and set their URLs. Then run migrations,
seed/import and Streamlit. The helper is Windows-specific; the Python application
and schema do not require Windows. Linux and production portability are unverified.

Local data is under `work/postgres-data`; do not synchronize/copy this live database
as a backup. Stop it before moving the workspace. Originals and generated data
are not uploaded to the private repository automatically.

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
an explicit owner-reviewed type correction during import without approving pages
or equipment applicability. Individual source download
URLs were not supplied; provenance records say so instead of inventing URLs.

## Tests — one command

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The full suite requires the project PostgreSQL server and `TEST_DATABASE_URL`.
Tests reject a database without a `_test` suffix or one matching development.
Each integration test migrates a unique schema and removes only that schema.
Unit and scope regression tests do not use the development database. UI tests use
Streamlit AppTest. Real free-text intent detection and ten maintenance conversations
belong to later phases; scope tests currently validate explicit equipment selection.

For a fresh environment verification, create another environment using the same
lock (`UV_PROJECT_ENVIRONMENT=work/repro-venv` with `uv sync --frozen --link-mode=copy`) and run its
Python against the same test command. Environment-specific secrets stay in `.env`.
If automatic Python installation fails, supply the full path to an existing
Python 3.12.14 using `uv sync --frozen --link-mode=copy --python <path>`.

## Structure

| Path | Responsibility |
|---|---|
| `app.py` | Spanish Streamlit catalog |
| `src/technicalnexus/` | Configuration, contracts, scope, PDF extraction, DB access |
| `migrations/` | Immutable Alembic schema revisions |
| `data/document_manifest.json` | Proposed titles, editions and applicability notes |
| `tests/` | Unit, selection regression, PostgreSQL integration and UI checks |
| `outputs/avance1roadmap.md` | Active English plan and milestone status |
| `NotaAcademica.md` | Living academic draft, source material for the final report |
| `docs/` | Source inventory, test evidence and user acceptance checklist |

## Storage and future integration

PostgreSQL stores catalog, page text, applicability and reviewed-answer relationships.
PDFs, images and model weights remain external, referenced by stable IDs/paths/hashes.
The local bootstrap account is a development owner, not a production application
role. Production needs a restricted role, hosted persistent PostgreSQL, backup
policy and a continuously available Flask host.

pgvector is not available in the current PostgreSQL installation and is not needed
for phase 1. Future embeddings can reference existing pages/fragments with model,
version and dimension metadata; no SQLite-to-PostgreSQL migration is planned.
RAG remains optional. Required later: TF-IDF/BoW + NB/SVM, ResNet50/EfficientNet,
agent coordination and Flask. Streamlit Community Cloud will host the GUI and
Cloudflare Tunnel will expose the later Flask service; a tunnel is not hosting.

Repository: https://github.com/Praxisinfinitum/TechnicalNexus (private).
See `docs/user-validation.md` for three owner checks before accepting this phase.
