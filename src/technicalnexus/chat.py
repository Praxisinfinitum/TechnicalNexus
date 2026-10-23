"""Immutable per-user presentation state. No Streamlit or database dependency."""
from dataclasses import dataclass, field
from typing import Callable, Literal
from technicalnexus.contracts import ConversationContext, EngineResponse, QueryRequest, SourceReference
from technicalnexus.i18n import translate
from technicalnexus.scope import EQUIPMENT_LABELS, select_equipment

@dataclass(frozen=True)
class ChatMessage:
    role: Literal["user", "assistant"]
    text: str
    references: tuple[SourceReference, ...] = ()
    status: str | None = None
    intent_id: str | None = None

@dataclass(frozen=True)
class ChatState:
    context: ConversationContext = field(default_factory=ConversationContext)
    messages: tuple[ChatMessage, ...] = ()

Responder = Callable[[QueryRequest], EngineResponse]

def submit_message(state: ChatState, text: str, responder: Responder) -> ChatState:
    response = responder(QueryRequest(text, state.context))
    if response.intent_id == "reset":
        return ChatState(response.context, (ChatMessage("assistant", translate("ui_reset_done"),
            status=response.status.value, intent_id="reset"),))
    previous = state.messages
    if (state.context.equipment_id is not None and response.context.equipment_id is not None
            and state.context.equipment_id != response.context.equipment_id):
        previous = ()  # Typed model changes start a new case, like the selector.
    return ChatState(response.context, previous + (
        ChatMessage("user", text),
        ChatMessage("assistant", response.text, response.references, response.status.value, response.intent_id),
    ))

def choose_equipment(state: ChatState, equipment_id: str | None, responder: Responder) -> ChatState:
    if equipment_id == state.context.equipment_id:
        return state
    if equipment_id is None:
        return ChatState(messages=(ChatMessage("assistant", translate("engine_select")),))
    context = select_equipment(ConversationContext(), equipment_id)
    if state.context.equipment_id is None and state.context.pending_fields:
        return submit_message(state, EQUIPMENT_LABELS[equipment_id], responder)
    notice = translate("ui_equipment_changed").format(model=EQUIPMENT_LABELS[equipment_id])
    return ChatState(context, (ChatMessage("assistant", notice,
        status="answer", intent_id="select_equipment"),))
