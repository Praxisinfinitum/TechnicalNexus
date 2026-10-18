import pytest
from technicalnexus.chat import ChatMessage, ChatState, choose_equipment, submit_message
from technicalnexus.contracts import ConversationContext, EngineResponse, ResponseStatus

def responder(request):
    return EngineResponse(ResponseStatus.ANSWER, "selected", "Respuesta", ConversationContext(equipment_id="brother_dcp_t430w"))

def test_submit_preserves_original_state_and_appends_turn():
    old = ChatState()
    new = submit_message(old, "Brother DCP-T430W", responder)
    assert not old.messages and old.context.equipment_id is None
    assert [m.role for m in new.messages] == ["user", "assistant"]
    assert new.context.equipment_id == "brother_dcp_t430w"

def test_selector_reset_clears_technical_history_and_pending_state():
    old = ChatState(ConversationContext(equipment_id="brother_dcp_t430w", pending_fields=("intent:ink_level",)),
        (ChatMessage("assistant", "old technical content"),))
    new = choose_equipment(old, None, responder)
    assert new.context == ConversationContext()
    assert "old technical content" not in str(new.messages)
    assert old.context.equipment_id == "brother_dcp_t430w"

def test_selector_can_answer_pending_equipment_question():
    old = ChatState(ConversationContext(pending_fields=("intent:ink_level",)))
    observed = []
    def pending_responder(request):
        observed.append(request)
        return responder(request)
    new = choose_equipment(old, "brother_dcp_t430w", pending_responder)
    assert observed[0].context.pending_fields == ("intent:ink_level",)
    assert new.context.equipment_id == "brother_dcp_t430w"
    with pytest.raises(ValueError):
        choose_equipment(old, "unknown_device", pending_responder)

def test_typed_reset_clears_history_as_well_as_context():
    old = ChatState(ConversationContext(equipment_id="brother_dcp_t430w"),
        (ChatMessage("assistant", "old answer"),))
    def reset_responder(request):
        return EngineResponse(ResponseStatus.ANSWER, "reset", "Caso reiniciado", ConversationContext())
    new = submit_message(old, "reiniciar", reset_responder)
    assert new.context == ConversationContext()
    assert len(new.messages) == 1 and "old answer" not in str(new.messages)
