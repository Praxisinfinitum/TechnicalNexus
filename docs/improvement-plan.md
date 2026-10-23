# Continuation and improvement plan

## Before declaring Advance 1 ready for submission

The owner-selected three printers are integrated as of 2026-10-22. Current code
contains 19 reviewed answers, and the evaluation covers 38 conversations/97 turns.
The earlier single-model milestone is preserved in Git and phase evidence.

1. Owner performs the three short model-expansion checks in user-validation.md.
2. Assemble the actual Advance-1 academic document from the draft and evidence.
3. Confirm instructor access to private code/materials. Do not publish licensed PDFs.
4. Keep the facilitator's Colab clarification separate from the originally read page.

## Observed limitations and concrete improvements

| Observation | Improvement | Validation |
|---|---|---|
| Finite rules need explicit phrasing; “normal” initially matched an overbroad normative rule and was corrected during phase 2. | Keep those regression cases; collect owner phrasing and train the required NB/SVM intent model later. Retain independent source/approval gates. | Unseen paraphrase evaluation with per-intent metrics and explicit ambiguous/out-of-domain cases. |
| Three scopes now have different procedures and a finite approved knowledge set. | Expand only with explicit source/region review; keep Canon ink/head-cleaning unsupported until appropriate evidence exists. | Preserve model-switch, mixed-model, source revocation and differing jam/refill cases. |
| The simulated unavailable DB turn took about 9 seconds; normal AppTest turns averaged about 140 ms in this run. These are framework/UI timings, not isolated inference latency. | Avoid repeated health/catalog queries during a single chat rerun; use a bounded health status strategy and review connection timeouts. Do not add an unsourced answer fallback. | Repeat the identical failure/recovery scenario and compare measured duration while preserving history, context and secret redaction. |
| Multicolumn/multilingual PDF extraction is not a faithful layout representation; three pages were empty and one flagged in the initial inventory. | Continue visual section review; add OCR/layout-aware processing only when necessary, preserving raw text and exact version/page. | Sample comparison with original pages, language separation and anchor/version checks. |
| Jam guidance intentionally points to diagrams instead of inventing a complete repair sequence. | Review any fuller procedure from an applicable official user guide before adding it. | Source-backed step review, user confirmation and regression; no unattended physical repair claims. |
| Chat is session-local and not durable across every refresh/restart. | Add persistence only if a real requirement appears; define retention/privacy first. | Explicit lifecycle and user/session authorization tests. |

## Required Advance 2 — week 5

- Intent dataset with provenance and proper train/test separation; tokenization,
  normalization, stopwords, stemming/lemmatization and TF-IDF or Bag of Words.
- Naive Bayes or SVM with per-intent evaluation grounded in actual runs.
- A domain-relevant permitted image dataset; ResNet50 or EfficientNet transfer
  learning with accuracy, precision, recall, F1 and confusion matrix. Group related
  captures/augmentations to avoid leakage.
- Initial multimodal coordination: classification contributes to the same printer
  assistance case. An image class is not root-cause diagnosis or model identity.
- No suitable printer dataset has been selected; feasibility is an early action,
  not a result to assume from the availability of PDF manuals.

## Required final — weeks 6–8

- Add reactive/deliberative/hybrid agent coordination and a real Flask REST adapter
  used by Streamlit. Reuse engine contracts and repository gates.
- Streamlit Community Cloud plus Cloudflare Tunnel as agreed. Choose persistent
  Flask/PostgreSQL/asset hosting; the tunnel does not provide those hosts.
- Error monitoring, ethical/privacy analysis and integrated performance,
  scalability and maintainability evaluation based on evidence.
- Prepare 15–20-page technical document, 5–10-minute demo, public URL, GitHub,
  architecture, testing/deployment evidence, classification/chatbot metrics and
  improvement plan. Reserve week 8 for integration/review/correction/delivery.
- RAG/pgvector remains optional and must not displace required classifier work.
