import pytest
from technicalnexus.contracts import ConversationContext, QueryRequest, SourceReference
from technicalnexus.engine import RulesEngine
from technicalnexus.knowledge import ReviewedAnswer

class ScopedRepository:
    def __init__(self):
        self.calls = []

    def find(self, instance, equipment, intent, language):
        self.calls.append((equipment, intent))
        if (equipment == "canon_c3935i" and intent in {"ink_level", "print_quality"}) or (
                equipment.startswith("brother") and intent == "toner_level"):
            return None
        return ReviewedAnswer(equipment, "", (SourceReference(equipment, 1),))

@pytest.mark.parametrize("query,equipment,intent", [
    ("Brother DCP-T220 nivel de tinta", "brother_dcp_t220", "ink_level"),
    ("T220 limpieza de cabezales", "brother_dcp_t220", "print_quality"),
    ("Canon imageRUNNER ADVANCE DX C3935i nivel de tóner", "canon_c3935i", "toner_level"),
    ("C3935i limpiar el cristal", "canon_c3935i", "glass_cleaning"),
    ("DCP-T430W nivel tinta", "brother_dcp_t430w", "ink_level"),
])
def test_explicit_model_switch_uses_only_new_equipment(query, equipment, intent):
    repo = ScopedRepository()
    response = RulesEngine(repo).respond(QueryRequest(query, ConversationContext(
        equipment_id="brother_dcp_t430w", pending_fields=("intent:paper_jam",))))
    assert response.context.equipment_id == equipment and not response.context.pending_fields
    assert response.intent_id == intent and response.references[0].document_id == equipment
    assert repo.calls == [(equipment, intent)]

@pytest.mark.parametrize("query", [
    "Compara DCP-T220 y DCP-T430W", "C3935i y T220 atasco de papel",
    "Canon DCP-T220", "Brother C3935i", "DCP-T220 y Epson L3250", "Canon C3930i nivel de tóner",
    "Brother DCP-T220W nivel de tinta",
])
def test_mixed_or_unapproved_models_clear_context_without_knowledge_lookup(query):
    repo = ScopedRepository()
    result = RulesEngine(repo).respond(QueryRequest(query, ConversationContext(equipment_id="brother_dcp_t220")))
    assert result.intent_id == "unsupported_equipment"
    assert result.context == ConversationContext() and not repo.calls

@pytest.mark.parametrize("equipment,query", [
    ("canon_c3935i", "Nivel de tinta"), ("canon_c3935i", "Limpieza normal del cabezal"),
    ("brother_dcp_t220", "Nivel de tóner"),
])
def test_missing_procedure_never_falls_back_to_another_equipment(equipment, query):
    result = RulesEngine(ScopedRepository()).respond(QueryRequest(query, ConversationContext(equipment_id=equipment)))
    assert result.status == "no_evidence" and not result.references

def test_pending_question_resumes_on_selected_model_only():
    engine = RulesEngine(ScopedRepository())
    pending = engine.respond(QueryRequest("Nivel de tóner"))
    response = engine.respond(QueryRequest("Canon C3935i", pending.context))
    assert response.references[0].document_id == "canon_c3935i"
    changed = engine.respond(QueryRequest("Brother", response.context))
    assert changed.context == ConversationContext()
