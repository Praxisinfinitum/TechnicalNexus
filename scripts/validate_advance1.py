"""Reproduce Advance-1 GUI evidence using real reviewed sources in a fresh test schema.

No development data is modified. Requires the locally supplied PDF originals.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter
from uuid import uuid4
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from streamlit.testing.v1 import AppTest
from technicalnexus.config import ROOT, Settings
from technicalnexus.database import engine_for, seed_catalog
from technicalnexus.documents import document_path, import_pdf
from technicalnexus.knowledge import load_all_reviewed_knowledge, reviewed_manifest_paths
from technicalnexus.scope import KNOWN_EQUIPMENT
from technicalnexus.models import Answer, Document, Page

CASES = ROOT / "data/validation/advance1-conversations.json"
REPORT = ROOT / "docs/advance1-conversations.json"
SUMMARY = ROOT / "docs/advance1-validation.md"

def code_fingerprint():
    paths = [ROOT / "app.py", ROOT / "uv.lock", Path(__file__), CASES,
        ROOT / "data/reviewed_knowledge.json", ROOT / "data/document_manifest.json"]
    paths += sorted((ROOT / "src").rglob("*.py"))
    paths += list(reviewed_manifest_paths(ROOT))
    paths += sorted((ROOT / "migrations").rglob("*.py"))
    digest = sha256()
    for path in sorted(set(paths)):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()

@contextmanager
def fresh_reviewed_database():
    settings = Settings.load()
    raw_test = os.environ.get("TEST_DATABASE_URL")
    if not raw_test:
        raise ValueError("TEST_DATABASE_URL is required")
    test_url, dev_url = make_url(raw_test), make_url(settings.database_url)
    if not (test_url.database or "").endswith("_test") or (
        test_url.host, test_url.port, test_url.database) == (dev_url.host, dev_url.port, dev_url.database):
        raise ValueError("Use a dedicated *_test database separate from development")
    schema = "validation_" + uuid4().hex
    control_engine = engine_for(raw_test)
    prior = os.environ.get("DATABASE_URL")
    with control_engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    scoped = test_url.update_query_dict({"options": f"-csearch_path={schema}"}).render_as_string(hide_password=False)
    os.environ["DATABASE_URL"] = scoped
    setup_started = perf_counter()
    try:
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
        engine = engine_for(scoped)
        try:
            with Session(engine) as session:
                seed_catalog(session)
                for entry in json.loads((ROOT / "data/document_manifest.json").read_text(encoding="utf-8")):
                    import_pdf(session, document_path(settings, entry, ROOT), entry, ROOT)
                load_all_reviewed_knowledge(session, ROOT)
                session.commit()
                setup = {"schema_revision": "0002", "postgresql_version": session.scalar(text("SHOW server_version")),
                    "documents": session.scalar(select(func.count()).select_from(Document)),
                    "pages": session.scalar(select(func.count()).select_from(Page)),
                    "approved_answers": session.scalar(select(func.count()).select_from(Answer).where(Answer.approved.is_(True))),
                    "setup_elapsed_ms": round((perf_counter() - setup_started) * 1000, 2)}
            yield scoped, setup
        finally:
            engine.dispose()
    finally:
        if prior is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = prior
        # Generated schema only; never drop tables in the development schema.
        with control_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        control_engine.dispose()

def execute_case(case, scoped):
    ui = AppTest.from_file(str(ROOT / "app.py")).run(timeout=30)
    if ui.exception:
        raise RuntimeError("GUI startup failed")
    records = []
    for step in case["steps"]:
        started = perf_counter()
        if step.get("simulate_database_failure"):
            os.environ["DATABASE_URL"] = "postgresql+psycopg://test:unusable@127.0.0.1:1/missing"
        try:
            if "select_equipment" in step:
                ui.selectbox(key="equipment_choice").set_value(step["select_equipment"]).run(timeout=30)
            elif "guided_intent" in step:
                from technicalnexus.guidance import OPTIONS
                option = next(option for option in OPTIONS if option.intent_id == step["guided_intent"])
                ui.selectbox(key="guide_topic").set_value(option.topic).run(timeout=30)
                ui.selectbox(key="guide_question").set_value(option.intent_id).run(timeout=30)
                ui.button(key="guide_submit").click().run(timeout=30)
            else:
                ui.chat_input[0].set_value(step["input"]).run(timeout=30)
        finally:
            os.environ["DATABASE_URL"] = scoped
        state = ui.session_state["conversation"]
        actual = state.messages[-1]
        pages = [ref.page_number for ref in actual.references]
        captions = [caption.value for caption in ui.caption]
        checks = {
            "no_ui_exception": not bool(ui.exception),
            "status": actual.status == step["expected_status"],
            "intent": actual.intent_id == step["expected_intent"],
            "source_pages": pages == step["expected_pages"],
            "equipment": state.context.equipment_id == step["expected_equipment"],
            "visible_references": all(any(f"pág. {page}" in caption and "Fuente:" in caption for caption in captions) for page in pages),
            "model_specific_text": all(part in actual.text for part in step.get("expected_text_contains", [])),
        }
        route = "equipment_selector" if "select_equipment" in step else "guided" if "guided_intent" in step else "free_text"
        records.append({"input": step["input"], "route": route, "expected": {k.removeprefix("expected_"): v for k, v in step.items() if k.startswith("expected_")},
            "actual": {"status": actual.status, "intent": actual.intent_id, "response": actual.text,
                "equipment": state.context.equipment_id, "references": [
                    {"file": ref.filename, "document_sha256": ref.document_id, "page": ref.page_number,
                     "section": ref.section} for ref in actual.references]},
            "ui_test_elapsed_ms": round((perf_counter() - started) * 1000, 2),
            "simulated_database_failure": step.get("simulate_database_failure", False),
            "checks": checks, "passed": all(checks.values())})
    return {"id": case["id"], "user_need": case["user_need"], "turns": records,
        "passed": all(turn["passed"] for turn in records)}

def write_report(results, setup):
    turns = [turn for case in results for turn in case["turns"]]
    latencies = sorted(turn["ui_test_elapsed_ms"] for turn in turns)
    git_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    report = {"kind": "agent_executed_streamlit_apptest_with_real_postgresql_and_sources",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "base_git_commit": git_commit, "code_and_inputs_sha256": code_fingerprint(),
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
            "packages": {p: version(p) for p in ["streamlit", "nltk", "sqlalchemy", "psycopg", "pypdf"]}},
        "scope": {"supported_equipment": sorted(KNOWN_EQUIPMENT), "other_two_models": "integrated with bounded reviewed knowledge",
            "owner_validation": "pending", "test_schema": "fresh migrated schema, removed after run"},
        "setup": setup, "summary": {"conversations": len(results),
            "passed_conversations": sum(case["passed"] for case in results), "turns": len(turns),
            "passed_turns": sum(turn["passed"] for turn in turns),
            "mean_ui_test_ms": round(sum(latencies) / len(latencies), 2),
            "minimum_ui_test_ms": min(latencies), "maximum_ui_test_ms": max(latencies)},
        "cases": results}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Advance 1 — functional validation", "", "Status: executed for Brother DCP-T430W, Brother DCP-T220 and Canon C3935i. Owner acceptance of the expanded scope remains pending.", "",
        f"Execution (UTC): {report['executed_at_utc']}", f"Base code commit: `{git_commit}`. Exact code/input fingerprint: `{report['code_and_inputs_sha256']}`.", "",
        "This is real Streamlit AppTest execution against newly migrated PostgreSQL with the supplied PDF originals and reviewed knowledge. It is not a synthetic-answer fixture, physical printer trial or manual browser run.", "",
        f"Result: **{report['summary']['passed_conversations']}/{len(results)} conversations; {report['summary']['passed_turns']}/{len(turns)} turns passed the predefined checks.**", "",
        "Each conversation starts with independent session state. Expected results were authored in data/validation/advance1-conversations.json before execution. Full inputs, actual responses, references and per-turn checks are in [the JSON evidence](advance1-conversations.json).", "",
        "| Case | User need | Turns | Result |", "|---|---|---:|---|"]
    for case in results:
        lines.append(f"| {case['id']} | {case['user_need']} | {len(case['turns'])} | {'PASS' if case['passed'] else 'FAIL'} |")
    lines += ["", "## Method and limits", "",
        "Checks compare intent, status, active equipment, physical source pages and visible reference captions; GUI exceptions fail the case. The fixed expected set is a functional acceptance set, not an independent corpus for model accuracy. Passing these cases does not demonstrate arbitrary-language correctness or repaired hardware.", "",
        f"Fresh schema reconstruction/import: {setup['documents']} documents, {setup['pages']} pages, {setup['approved_answers']} reviewed answers; PostgreSQL {setup['postgresql_version']}, revision {setup['schema_revision']}.",
        "Development data was not modified; the generated validation schema was removed after execution. No passwords or database URLs are included in the evidence.", "",
        f"Measured AppTest rerun duration: mean {report['summary']['mean_ui_test_ms']} ms, range {min(latencies)}–{max(latencies)} ms. This includes UI test/framework work and database requests; it is not isolated inference latency, a browser/network benchmark, or a load/scalability test.", "",
        "Cases include model-specific technical/navigation topics, missing context, ambiguity/negation, another department, absent normative knowledge, unsupported models, reset and closure. C17 simulates an unavailable DB endpoint then restores the same test schema. Expanded cases exercise all three printers and switches between supported models, including different jam precautions and intentionally unsupported ink/head-cleaning requests on Canon.", "",
        "Separate unit/integration regression covers unsupported contract languages and source-approval failures. Owner review and physical printer verification are not inferred from these executions.", ""]
    for case in results:
        lines += [f"## {case['id']} — {case['user_need']}", ""]
        for number, turn in enumerate(case["turns"], 1):
            lines += [f"### Turn {number}", "", f"User: {turn['input']}", "", "Assistant:", "", turn["actual"]["response"], ""]
            for ref in turn["actual"]["references"]:
                lines += [f"Source: {ref['file']}, physical page {ref['page']} — {ref['section']}.", ""]
            lines += [f"Expected/actual: {turn['expected']['intent']}/{turn['actual']['intent']}; {turn['expected']['status']}/{turn['actual']['status']}. Result: {'PASS' if turn['passed'] else 'FAIL'}.", ""]
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    return report

def main():
    started = perf_counter()
    with fresh_reviewed_database() as (scoped, setup):
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        if len(cases) < 10 or len({case["id"] for case in cases}) != len(cases):
            raise ValueError("At least ten unique conversation cases are required")
        results = [execute_case(case, scoped) for case in cases]
        report = write_report(results, setup)
    print(json.dumps({"summary": report["summary"], "elapsed_seconds": round(perf_counter()-started, 2),
        "report": "docs/advance1-validation.md"}))
    if not all(case["passed"] for case in results):
        sys.exit(1)

if __name__ == "__main__": main()
