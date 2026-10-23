# TechnicalNexus — Advance 1 review package

**Prepared for Brother DCP-T430W, Brother DCP-T220 and Canon imageRUNNER ADVANCE DX
C3935i.** The three selected models have bounded reviewed knowledge. Earlier
phases were owner-accepted for T430W; owner acceptance of the new models and the
academic package remains pending. This package is source material, not the finished
academic deliverable. See [model-expansion.md](model-expansion.md).

## Review route

1. Read [README](../README.md): features, reproducible setup, running the web app,
   history/reset/source behavior and limits.
2. Read [NotaAcademica](../NotaAcademica.md): living instructor-facing draft of the
   problem, objective, users, architecture and actual development stages.
3. Inspect the [architecture SVG](architecture/current.svg) or editable
   [Mermaid source](architecture/current.mmd), and [intent flows](intents-and-flows.md).
4. Review [38-conversation validation](advance1-validation.md), including actual
   responses, and [machine-readable evidence](advance1-conversations.json).
5. Confirm [owner validation](user-validation.md), [source inventory](source-inventory.md)
   and [future improvements](improvement-plan.md).

## Rubric-to-evidence mapping

| Criterion | Points | Evidence and practical limit |
|---|---:|---|
| Problem and justification | 20 | NotaAcademica: situation, affected users, need, objective, scope and expected benefits. Rules are an AI course baseline; user time/error savings are hypotheses, not measured benefits. |
| Conceptual architecture | 20 | Current SVG/Mermaid and academic draft: user, chatbot, knowledge base, conversation and data exchanges. Final CNN/agent/API diagram is explicitly future work. |
| Intents and conversation flow | 20 | intents-and-flows.md maps every defined intent/control/error to input → identification → response. GUI validation covers user-reachable flows; unsupported contract language is checked by automated regression. |
| Rules implementation | 25 | Python 3.12.14, NLTK tokenization and deterministic rules; Streamlit adapter and PostgreSQL gates; private GitHub code. Colab omitted by the owner's explicit clarification, despite its mention in the originally read page. |
| Tests and analysis | 15 | 38 independent GUI conversations, 97 input/response turns, exact source pages and expected/actual checks; fresh-schema import; latest expanded suite: 97 passing tests in .venv (previous clean-environment run: 66 tests). Model-specific procedure limits and phrase limitations remain explicit. |

Private source repository: https://github.com/Praxisinfinitum/TechnicalNexus

Owner access through GitHub CLI can be checked without changing repository visibility.
Instructor access has not been proven: a private repository link is not accessible
to every viewer. Arrange the instructor's intended access or permitted code export
before submission; do not make the repository public by default.

## Reproduce the evidence

After README setup, run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/validate_advance1.py
```

The second command uses the supplied PDF originals to migrate, import and seed a
fresh unique schema in the separate `_test` database. It then runs the real Streamlit
AppTest UI and writes actual results to the two validation files. It never uses the
development schema for cleanup; its own generated schema is removed afterward.
Original PDFs, `.env`, local tools and live database files remain outside Git.

## Deliverable boundaries

- NotaAcademica.md stays a living draft for the final project. This is not the final
  15–20-page report, 5–10-minute video or cloud deployment package.
- No trained text/image classifier metrics, physical repairs, production load test,
  universally safe language handling or multi-tenant security is claimed.
- All three selected models are integrated; broader procedures and owner acceptance remain pending.
- The student reviews, understands and submits personally in Canvas. No submission
  or authorship declaration has been performed by the agent.
