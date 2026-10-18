"""Relational source catalog; extraction is not answer approval."""
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass

class Instance(Base):
    __tablename__ = "instances"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))

class Equipment(Base):
    __tablename__ = "equipment"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    instance_id: Mapped[str] = mapped_column(ForeignKey("instances.id"))
    brand: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # SHA-256 of original bytes
    original_filename: Mapped[str] = mapped_column(String(255))
    relative_path: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    document_type: Mapped[str] = mapped_column(String(80))
    language: Mapped[str] = mapped_column(String(30))
    edition: Mapped[str] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance: Mapped[str] = mapped_column(Text)
    page_count: Mapped[int] = mapped_column(Integer)
    classification_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (CheckConstraint("page_count > 0"),)

class Applicability(Base):
    __tablename__ = "document_equipment"
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), primary_key=True)
    equipment_id: Mapped[str] = mapped_column(ForeignKey("equipment.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(30), default="pending")
    evidence: Mapped[str] = mapped_column(Text, default="")
    __table_args__ = (CheckConstraint("status IN ('pending', 'confirmed', 'excluded')"),)

class Page(Base):
    __tablename__ = "document_pages"
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"))
    page_number: Mapped[int] = mapped_column(Integer)
    raw_text: Mapped[str] = mapped_column(Text)
    normalized_text: Mapped[str] = mapped_column(Text)
    extraction_status: Mapped[str] = mapped_column(String(30))
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("document_id", "page_number"), CheckConstraint("page_number > 0"))

class Intent(Base):
    __tablename__ = "intents"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    instance_id: Mapped[str] = mapped_column(ForeignKey("instances.id"))
    description: Mapped[str] = mapped_column(Text)

class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[str] = mapped_column(ForeignKey("equipment.id"))
    intent_id: Mapped[str] = mapped_column(ForeignKey("intents.id"))
    language: Mapped[str] = mapped_column(String(10), default="es")
    text: Mapped[str] = mapped_column(Text)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    conditions: Mapped[str] = mapped_column(Text, default="")
    review_note: Mapped[str] = mapped_column(Text, default="")
    __table_args__ = (UniqueConstraint("equipment_id", "intent_id", "language", name="uq_answer_scope"),)

class AnswerSource(Base):
    __tablename__ = "answer_sources"
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"), primary_key=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("document_pages.id"), primary_key=True)
    section: Mapped[str] = mapped_column(Text, default="")
