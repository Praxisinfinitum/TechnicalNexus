import pytest
from technicalnexus.contracts import ConversationContext, QueryRequest, SourceReference
from technicalnexus.engine import RulesEngine, normalize_query
from technicalnexus.knowledge import ReviewedAnswer

class FakeRepository:
    def __init__(self, fail=False, missing=False):
        self.calls = []
        self.fail = fail
        self.missing = missing

    def find(self, *args):
        self.calls.append(args)
        if self.fail:
            raise RuntimeError("private internal connection detail")
        if self.missing:
            return None
        return ReviewedAnswer("Respuesta revisada", "Sólo para el equipo confirmado.",
            (SourceReference("test_hash", 3, "reference.pdf", "Guía", "Tinta"),))

def test_nltk_normalization_preserves_negation_and_separates_model():
    assert normalize_query("NO hay papel; DCP-T430W") == "no hay papel dcp t 430 w"
    assert normalize_query("¿Cómo LIMPIAR el cabezal?") == "como limpiar el cabezal"

def test_missing_device_can_resume_one_pending_intent():
    repo = FakeRepository()
    engine = RulesEngine(repo)
    first = engine.respond(QueryRequest("¿Cómo compruebo el nivel de tinta?"))
    assert first.status == "clarification" and not repo.calls
    second = engine.respond(QueryRequest("Brother DCP-T430W", first.context))
    assert second.intent_id == "ink_level" and second.references[0].page_number == 3
    assert second.context.pending_fields == ()

def test_unknown_device_clears_previous_technical_context():
    engine = RulesEngine(FakeRepository())
    response = engine.respond(QueryRequest("Ahora una Epson L3250", ConversationContext(
        equipment_id="brother_dcp_t430w", pending_fields=("intent:ink_level",))))
    assert response.status == "out_of_scope" and response.context == ConversationContext()

@pytest.mark.parametrize("failure,missing,status", [(True, False, "error"), (False, True, "no_evidence")])
def test_unavailable_repository_never_invents_an_answer(failure, missing, status):
    engine = RulesEngine(FakeRepository(fail=failure, missing=missing))
    response = engine.respond(QueryRequest("Nivel de tinta", ConversationContext(equipment_id="brother_dcp_t430w")))
    assert response.status == status and not response.references
    assert "private" not in response.text

def test_independent_sessions_do_not_share_selection():
    engine = RulesEngine(FakeRepository())
    first = engine.respond(QueryRequest("DCP-T430W"))
    second = engine.respond(QueryRequest("Nivel de tinta"))
    assert first.context.equipment_id == "brother_dcp_t430w"
    assert second.status == "clarification" and second.context.equipment_id is None
