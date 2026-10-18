# Phase 1 — owner validation (pending)

These three checks take approximately 5–10 minutes total. Automated tests have
already been executed. Do not mark these accepted until the owner reports results.

| Check | Steps | Expected result | Owner result |
|---|---|---|---|
| 1. Equipment and source inventory | Read `docs/source-inventory.md`, compare the reference-guide title with the original PDF, and confirm Brother is the intended first model. | Ten original filenames preserved; pending applicability clearly marked; two models still undecided. | Pending |
| 2. Objective and architecture | Read the problem and implemented diagram in `NotaAcademica.md`. | Local GUI, Python boundary and PostgreSQL are understandable; no completed chatbot, automatic source approval or visual model is claimed. | Pending |
| 3. Initial app | Open http://localhost:8501; if stopped, follow README startup. Inspect the model, catalog and phase notice. | Spanish presentation, Brother DCP-T430W, ten catalog entries and a clear statement that chatbot work begins in phase 2. | Pending |

Please report: accepted, or the check number and observed issue. No need to rerun
all unit tests manually. Minor wording requests can become backlog items; incorrect
scope, unreadable architecture or startup failure must be corrected before acceptance.
