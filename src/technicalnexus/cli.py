"""Small repeatable operations for the phase-1 source catalog."""
import argparse
import json
import sys
from sqlalchemy import text
from sqlalchemy.orm import Session
from technicalnexus.config import ROOT, Settings
from technicalnexus.database import engine_for, seed_catalog
from technicalnexus.documents import catalog_rows, import_pdf
from technicalnexus.scope import INSTANCE_ID
from technicalnexus.contracts import ConversationContext, QueryRequest
from technicalnexus.engine import RulesEngine
from technicalnexus.i18n import translate
from technicalnexus.knowledge import KnowledgeRepository, load_reviewed_knowledge

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["seed", "import-manuals", "catalog", "health", "seed-knowledge", "chat", "ask"])
    parser.add_argument("--text", help="A single Spanish query for the ask command")
    parser.add_argument("--equipment", choices=["brother_dcp_t430w"], help="Explicit equipment context for ask")
    args = parser.parse_args()
    if args.command == "ask" and not args.text:
        parser.error("ask requires --text")
    settings = Settings.load()
    with Session(engine_for(settings.database_url)) as session:
        if args.command == "health":
            print(json.dumps({"database": "ok", "version": session.scalar(text("SHOW server_version")),
                "pgvector_available": session.scalar(text("SELECT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name='vector')"))}))
        elif args.command == "seed":
            seed_catalog(session)
            session.commit()
            print("Catalog seed completed")
        elif args.command == "import-manuals":
            seed_catalog(session)
            metadata = json.loads((ROOT / "data/document_manifest.json").read_text(encoding="utf-8"))
            for entry in metadata:
                import_pdf(session, settings.manuals_path / entry["filename"], entry, ROOT)
            session.commit()
            print(f"Registered {len(metadata)} PDFs; no technical answers approved")
        elif args.command == "seed-knowledge":
            load_reviewed_knowledge(session, ROOT / "data/reviewed_knowledge.json", ROOT)
            session.commit()
            print("Reviewed Brother knowledge loaded; other sources remain unapproved")
        elif args.command in {"chat", "ask"}:
            engine = RulesEngine(KnowledgeRepository(session))
            context = ConversationContext(equipment_id=args.equipment)
            while True:
                try:
                    user_text = args.text if args.command == "ask" else input(translate("cli_prompt"))
                except (EOFError, KeyboardInterrupt):
                    break
                response = engine.respond(QueryRequest(user_text, context))
                context = response.context
                print(translate("cli_response"), response.text)
                for ref in response.references:
                    print(f"{translate('cli_source')}: {ref.filename}, p. {ref.page_number} — {ref.section}")
                if response.status.value == "error":
                    session.rollback()  # Permit retry after a transient database failure.
                if args.command == "ask" or response.intent_id == "goodbye":
                    break
        else:
            print(json.dumps(catalog_rows(session, INSTANCE_ID), ensure_ascii=True, indent=2))

if __name__ == "__main__": main()
