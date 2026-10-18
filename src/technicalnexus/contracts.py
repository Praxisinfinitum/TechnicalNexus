"""Stable conversation boundary independent of the GUI and database driver."""
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

class ResponseStatus(StrEnum):
    ANSWER = "answer"
    CLARIFICATION = "clarification"
    OUT_OF_SCOPE = "out_of_scope"
    NO_EVIDENCE = "no_evidence"
    ERROR = "error"

@dataclass(frozen=True)
class ConversationContext:
    instance_id: str = "office_printer_maintenance"
    equipment_id: str | None = None
    pending_fields: tuple[str, ...] = ()

@dataclass(frozen=True)
class QueryRequest:
    text: str
    context: ConversationContext = field(default_factory=ConversationContext)
    language: str = "es"

@dataclass(frozen=True)
class SourceReference:
    document_id: str
    page_number: int
    filename: str = ""
    title: str = ""
    section: str = ""

@dataclass(frozen=True)
class EngineResponse:
    status: ResponseStatus
    intent_id: str | None
    text: str
    context: ConversationContext
    references: tuple[SourceReference, ...] = ()

class ConversationEngine(Protocol):
    def respond(self, request: QueryRequest) -> EngineResponse: ...
