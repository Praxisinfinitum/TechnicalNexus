"""Record a small real PostgreSQL-backed CLI demonstration, not final user acceptance."""
import json
from pathlib import Path
from sqlalchemy.orm import Session
from technicalnexus.config import ROOT, Settings
from technicalnexus.contracts import ConversationContext, QueryRequest
from technicalnexus.database import engine_for
from technicalnexus.engine import RulesEngine
from technicalnexus.knowledge import KnowledgeRepository

SCENARIOS = {
    "clarify_and_resume": ["¿Cómo compruebo el nivel de tinta?", "Brother DCP-T430W", "Ya rellené la tinta"],
    "normal_maintenance": ["DCP-T430W", "Limpieza normal del cabezal", "No hay papel", "Bandeja no detectada"],
    "scope_boundaries": ["DCP-T430W", "¿Qué ISO aplica?", "¿Cómo calculo la nómina?", "Cambiar a Epson L3250", "Nivel de tinta"],
    "source_navigation": ["DCP-T430W", "Hay un atasco de papel", "¿Dónde está el manual?"],
    "reset_and_close": ["DCP-T430W", "reiniciar", "No hay papel", "adiós"],
}

def main():
    with Session(engine_for(Settings.load().database_url)) as session:
        engine = RulesEngine(KnowledgeRepository(session))
        records = []
        for name, inputs in SCENARIOS.items():
            context = ConversationContext()
            turns = []
            for message in inputs:
                response = engine.respond(QueryRequest(message, context))
                context = response.context
                turns.append({"input": message, "status": response.status.value, "intent": response.intent_id,
                    "response": response.text, "equipment_id": context.equipment_id,
                    "references": [{"document": ref.filename, "sha256": ref.document_id,
                        "page": ref.page_number, "section": ref.section} for ref in response.references]})
            records.append({"scenario": name, "turns": turns})
    destination = ROOT / "docs/phase2-demo.json"
    destination.write_text(json.dumps({"kind": "agent_executed_cli_demo", "date": "2026-10-17",
        "scenarios": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(records)} PostgreSQL-backed conversations in docs/phase2-demo.json")

if __name__ == "__main__": main()
