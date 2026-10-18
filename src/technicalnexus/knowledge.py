"""Reviewed knowledge repository. Fail closed if any required source is invalid."""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from technicalnexus.contracts import SourceReference
from technicalnexus.models import Answer, AnswerSource, Applicability, Document, Equipment, Intent, Page

@dataclass(frozen=True)
class ReviewedAnswer:
    text: str
    conditions: str
    references: tuple[SourceReference, ...]

class KnowledgeRepository:
    def __init__(self, session: Session):
        self.session = session

    def find(self, instance_id: str, equipment_id: str, intent_id: str, language: str) -> ReviewedAnswer | None:
        answer = self.session.scalar(select(Answer).join(Equipment).join(Intent, Intent.id == Answer.intent_id)
            .where(Answer.equipment_id == equipment_id, Answer.intent_id == intent_id,
                Answer.language == language, Answer.approved.is_(True),
                Equipment.instance_id == instance_id, Intent.instance_id == instance_id))
        if answer is None or not answer.review_note.strip():
            return None
        sources = list(self.session.scalars(select(AnswerSource).where(AnswerSource.answer_id == answer.id)))
        if not sources:
            return None
        references = []
        for source in sources:
            page = self.session.get(Page, source.page_id)
            if page is None or not page.approved or page.extraction_status != "extracted":
                return None
            applicability = self.session.get(Applicability, (page.document_id, equipment_id))
            if applicability is None or applicability.status != "confirmed":
                return None
            document = self.session.get(Document, page.document_id)
            if document is None or not source.section.strip():
                return None
            references.append(SourceReference(document.id, page.page_number,
                document.original_filename, document.title, source.section))
        return ReviewedAnswer(answer.text, answer.conditions, tuple(references))

def load_reviewed_knowledge(session: Session, path: Path, root: Path):
    """Apply an explicit, versioned review manifest. Does not approve other pages."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    equipment_id = payload["equipment_id"]
    equipment = session.get(Equipment, equipment_id)
    if equipment is None or equipment.instance_id != payload["instance_id"]:
        raise ValueError("Reviewed knowledge has an invalid equipment scope")
    for entry in payload["answers"]:
        resolved = []
        for source in entry["sources"]:
            document = session.get(Document, source["sha256"])
            if document is None or document.original_filename != source["filename"]:
                raise ValueError("Import the exact reviewed source before seeding answers")
            original = root / document.relative_path
            if sha256(original.read_bytes()).hexdigest() != document.id:
                raise ValueError("Original PDF differs from the reviewed version")
            page = session.scalar(select(Page).where(Page.document_id == document.id,
                Page.page_number == source["page"]))
            if page is None or page.extraction_status != "extracted":
                raise ValueError("Reviewed source page is missing or requires extraction review")
            if any(anchor.casefold() not in page.normalized_text.casefold() for anchor in source["anchors"]):
                raise ValueError("Reviewed text anchors do not match the source page")
            applicability = session.get(Applicability, (document.id, equipment_id))
            if applicability is None:
                raise ValueError("Missing equipment applicability review")
            applicability.status = "confirmed"
            applicability.evidence = payload["applicability_review"]
            page.approved = True
            resolved.append((page, source["section"]))
        session.merge(Intent(id=entry["intent_id"], instance_id=equipment.instance_id,
            description=entry["description"]))
        session.flush()
        answer = session.scalar(select(Answer).where(Answer.equipment_id == equipment_id,
            Answer.intent_id == entry["intent_id"], Answer.language == "es"))
        if answer is None:
            answer = Answer(equipment_id=equipment_id, intent_id=entry["intent_id"], language="es")
            session.add(answer)
        answer.text = entry["text"]
        answer.conditions = entry["conditions"]
        answer.review_note = payload["review_note"]
        answer.approved = True
        session.flush()
        expected = {p.id for p, _ in resolved}
        for old in session.scalars(select(AnswerSource).where(AnswerSource.answer_id == answer.id)):
            if old.page_id not in expected:
                session.delete(old)
        for page, section in resolved:
            session.merge(AnswerSource(answer_id=answer.id, page_id=page.id, section=section))
    session.flush()
