"""Conservative PDF extraction. No OCR, semantic search or automatic approval."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import unicodedata
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session
from technicalnexus.models import Applicability, Document, Equipment, Page

@dataclass(frozen=True)
class ExtractedPage:
    number: int
    raw_text: str
    normalized_text: str
    status: str

def normalize_text(text: str) -> str:
    # Preserve line boundaries, accented letters, negation and warning markers.
    text = unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))
    return "\n".join(re.sub(r"[^\S\n]+", " ", line).strip() for line in text.split("\n")).strip()

def extract_pages(path: Path) -> list[ExtractedPage]:
    result = []
    for number, page in enumerate(PdfReader(path).pages, 1):
        raw = page.extract_text() or ""
        text = normalize_text(raw)
        status = "empty" if not text else "review_required" if "\ufffd" in text else "extracted"
        result.append(ExtractedPage(number, raw, text, status))
    return result

def classify_document(text: str) -> str:
    sample = text.casefold()
    # A proposal, never a source authorization.
    patterns = [("licensing", "licensing remarks"), ("quick_setup", "configuración rápida"),
                ("product_safety", "lesiones personales"), ("network_security", "interfaces de red"),
                ("reference", "guía de consulta"), ("wifi_channels", "channels supported"),
                ("software_guide", "guía del usuario"), ("driver_guide", "controlador de impresión")]
    return next((kind for kind, marker in patterns if marker in sample), "unclassified")

def import_pdf(session: Session, path: Path, metadata: dict, project_root: Path) -> Document:
    equipment_id = metadata["equipment_id"]
    if session.get(Equipment, equipment_id) is None:
        raise ValueError("Unknown equipment")
    digest = sha256(path.read_bytes()).hexdigest()
    existing = session.get(Document, digest)
    if existing is not None:
        if session.get(Applicability, (digest, equipment_id)) is None:
            session.add(Applicability(document_id=digest, equipment_id=equipment_id, status="pending", evidence="Additional association requires review"))
        return existing
    pages = extract_pages(path)
    if not pages:
        raise ValueError("PDF contains no pages")
    document = Document(id=digest, original_filename=path.name,
        relative_path=path.resolve().relative_to(project_root.resolve()).as_posix(),
        title=metadata["title"], document_type=classify_document(pages[0].normalized_text),
        language=metadata["language"], edition=metadata["edition"], source_url=metadata.get("source_url"),
        provenance="User-provided local PDF; individual download URL not supplied", page_count=len(pages),
        classification_reviewed=False)
    session.add(document)
    session.flush()
    session.add(Applicability(document_id=digest, equipment_id=equipment_id,
        status="pending", evidence=metadata["applicability_note"]))
    for page in pages:
        session.add(Page(document_id=digest, page_number=page.number, raw_text=page.raw_text,
            normalized_text=page.normalized_text, extraction_status=page.status, approved=False))
    session.flush()
    return document

def catalog_rows(session: Session, instance_id: str) -> list[dict]:
    statement = (select(Document, Equipment).join(Applicability, Applicability.document_id == Document.id)
                 .join(Equipment, Equipment.id == Applicability.equipment_id)
                 .where(Equipment.instance_id == instance_id).order_by(Document.original_filename))
    return [{"model": e.model, "file": d.original_filename, "document": d.title,
             "pages": d.page_count, "type": d.document_type} for d, e in session.execute(statement)]
