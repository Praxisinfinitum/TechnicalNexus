"""Small repeatable operations for the phase-1 source catalog."""
import argparse
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from technicalnexus.config import ROOT, Settings
from technicalnexus.database import engine_for, seed_catalog
from technicalnexus.documents import catalog_rows, import_pdf
from technicalnexus.scope import INSTANCE_ID

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["seed", "import-manuals", "catalog", "health"])
    args = parser.parse_args()
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
        else:
            print(json.dumps(catalog_rows(session, INSTANCE_ID), ensure_ascii=True, indent=2))

if __name__ == "__main__": main()
