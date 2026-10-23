# Three-model integration review — 2026-10-22

Status: implemented and automatically validated. Owner acceptance of the expanded
scope and the Advance-1 review package remains pending. The actual academic
deliverable has not yet been assembled.

## Model-specific knowledge

| Equipment | ID | Reviewed answers | Main source |
|---|---|---:|---|
| Brother DCP-T430W | brother_dcp_t430w | 7 | Original reference-guide PDF, physical pp. 1–4 |
| Brother DCP-T220 | brother_dcp_t220 | 8 | DCP-T220_User_Guide_es-MX.pdf, 244 physical pages |
| Canon imageRUNNER ADVANCE DX C3935i | canon_c3935i | 4 | Canon_C3935i_User_Guide_es-ES.pdf, 1,687 physical pages |

T220 adds model-specific visible ink level (p. 193), completed-refill action
(p. 196), confirmed absent tray paper and incomplete tray insertion (p. 165),
normal panel head cleaning (p. 200), jam-procedure referral (p. 170), manual
location (p. 1) and scanner-glass cleaning (p. 199). Page numbers are physical,
not the printed numbering. T220 uses Inicio Negro/Color rather than the T430W's
Copia labels. Its post-refill action is not the T430W three-second combination.

Canon adds toner status (p. 145), glass cleaning (pp. 103–104), general jam
precautions (p. 148) and manual location (p. 1). Canon ink-tank/head-cleaning
queries have no evidence and never reuse Brother answers. No cartouche selection,
internal repair, optional-accessory procedure or regulatory answer is added.

## Source and regional review

The new PDF originals were obtained from official manufacturer sources on
2026-10-22. Every imported new source is pinned by SHA-256 in the document
manifest; answer seeding verifies original bytes and page text anchors. The
selected maintenance pages were read and rendered for review, with section
limits retained. The source review is agent-assisted; owner acceptance remains
pending and no manufacturer certification is implied.

Canon's PDF is European Spanish USRMA-8188-03, September 2025. The enabled three
maintenance procedures were compared with Latin America USRMA-8189-03:

- [Toner/consumables status](https://oip.manual.canon/USRMA-8189-zz-CS-3900-esLN/contents/devu-dev-mainte-consumables_remain.html)
- [Copy-glass cleaning](https://oip.manual.canon/USRMA-8189-zz-CS-3900-esLN/contents/devu-dev-mainte-clean-platen.html)
- [Paper-jam precautions](https://oip.manual.canon/USRMA-8189-zz-CS-3900-esLN/contents/devu-dev-papers_jam.html)

Only the matched guidance above is approved. Regional electrical requirements,
regulations, accessory compatibility and unrelated chapters remain unreviewed.
The cited PDF page is the stable offline reference. The owner accepted Canon's
personal/non-commercial download terms; originals remain local and excluded from
Git. Generic BRAdmin/driver guides are catalog material, not implicit network
capability or maintenance authorization for a printer.

## Application changes

- Shared admitted-model catalog powers database seeding, GUI labels and CLI choices.
- Explicit normalized aliases identify all three models; contradictory brands,
  mixed admitted models, unknown models and lookalike DCP-T220W clear context.
- Missing equipment can retain one pending intent; a fresh model change never
  carries a previous model's pending technical procedure.
- Selector and typed model changes clear previous supported-model history;
  guided topic/question state is also cleared when equipment changes.
- Guided choices and answers use the same live approval/source gates. Clicks
  enter the shared NLTK/rules service and recheck approval. Free text remains.
- Source catalog queries are filtered by selected equipment.
- New project-relative manifest paths resolve to the requested model folders;
  the original MANUALS_PATH override remains compatible. No new dependency,
  schema migration, vector search, generative model or deployment was introduced.

## Executed validation

**97 tests passed in 27.93 seconds** in the existing Python 3.12.14 locked
environment. **38 independent real-source GUI conversations / 97 turns passed**
predefined checks. The latest report records exact code/input fingerprint and
versions. The full test suite includes unit, regression, PostgreSQL integration
and Streamlit AppTest coverage.

Fresh-schema reconstruction imported 19 document/equipment associations, backed
by 16 unique PDF hashes / 2,197 pages, and seeded 19 reviewed answers. Three
identical software PDFs are shared storage identities with separate applicability.
The evaluation cleans only its generated schema in the dedicated test database.
No development cleanup or PDF redistribution took place.

Cases include guided queries for every new answer, supported-model switches,
opposite jam power precautions, distinct refill buttons, pending queries, Canon
ink/head-cleaning refusal, missing norms, mixed brands/models and near-name
rejection. Tests also cover source revocation, stale choices and independent
sessions. These are functional checks, not physical repairs, classifier metrics
or proof of arbitrary-language correctness. Database failure/recovery remains a
roughly nine-second scenario and is still an improvement target.

## Three short owner checks

1. Select DCP-T220. Consult post-refill and normal-cleaning options; confirm its
   button labels, conditions and references (physical pp. 196 and 200).
2. Switch to Canon. Confirm history/topic clear; consult toner and glass options,
   then type a head-cleaning request. Canon must not inherit Brother instructions.
3. Compare jam guidance by selecting Canon then T220 in separate cases. Canon
   says not to power off, whereas the T220 source procedure starts unplugged.
   Type “Compara DCP-T220 y C3935i”; it must reject the mixed scope and clear selection.

Owner result: pending. UI validation does not require performing physical maintenance.
See user-validation.md for the active checklist and historical acceptance records.
