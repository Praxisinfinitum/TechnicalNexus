# Phase 1 — owner validation

These three checks take approximately 5–10 minutes total. Automated tests have
already been executed. Do not mark these accepted until the owner reports results.

| Check | Steps | Expected result | Owner result |
|---|---|---|---|
| 1. Equipment and source inventory | Read `docs/source-inventory.md`, compare the reference-guide title with the original PDF, and confirm Brother is the intended first model. | Ten original filenames preserved; pending applicability clearly marked; two models still undecided. | Accepted by owner; document 6 type correction requested and implemented. |
| 2. Objective and architecture | Read the problem and implemented diagram in `NotaAcademica.md`. | Local GUI, Python boundary and PostgreSQL are understandable; no completed chatbot, automatic source approval or visual model is claimed. | Accepted by owner. |
| 3. Initial app | Open http://localhost:8501; if stopped, follow README startup. Inspect the model, catalog and phase notice. | Spanish presentation, Brother DCP-T430W, ten catalog entries and a clear statement that chatbot work begins in phase 2. | Accepted by owner after explanation of the verified PostgreSQL indicator. |

Please report: accepted, or the check number and observed issue. No need to rerun
all unit tests manually. Minor wording requests can become backlog items; incorrect
scope, unreadable architecture or startup failure must be corrected before acceptance.

## Phase 2 — accepted by owner

Start the CLI from the project root:

```powershell
.\.venv\Scripts\python.exe -m technicalnexus.cli chat
```

| Check | Inputs / action | Expected result | Owner result |
|---|---|---|---|
| 1. Documented answer | Enter `Nivel de tinta`, then `Brother DCP-T430W`; compare its source with reference-guide physical page 3. | Asks model first, then resumes ink-level topic with Spanish answer, limits and page reference. | Accepted; owner supplied matching CLI transcript. |
| 2. Knowledge boundaries | Enter `¿Qué norma ISO aplica?`, then `¿Cómo calculo la nómina?`. | No regulatory answer invented; HR request outside scope. Neither includes printer repair advice. | Accepted overall; ISO refusal observed in owner transcript. HR refusal covered by automated regression, not shown in manual transcript. |
| 3. Reset and model isolation | Enter `cambiar impresora`, `Epson L3250`, `Limpieza normal del cabezal`, then `DCP-T430W`. Finish with `adiós`. | Unsupported equipment rejected, no old context retained; requires supported model before cleaning, then cites page 4; close clears context. | Accepted; rejection, reset and resumed page-4 response observed. Exit used console interruption; goodbye not shown in manual transcript. |

Only Brother can be validated as supported today. This does not demonstrate switching
between two supported printers. The catalog web GUI has no chat input yet; phase 3
integrates the tested engine there. Report accepted or check number plus observation;
no need to rerun the automated suite manually.

Owner reported “Todo bien” and supplied the successful interactive CLI transcript. Summary: docs/phase2-owner-validation.md. Acceptance applies to the implemented Brother scope, not the two pending models or future GUI.
