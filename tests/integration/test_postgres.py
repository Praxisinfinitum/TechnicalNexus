import os
from pathlib import Path
from uuid import uuid4
import pytest
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from pypdf import PdfWriter
from technicalnexus.config import ROOT
from technicalnexus.database import engine_for, seed_catalog
from technicalnexus.documents import catalog_rows, import_pdf
from technicalnexus.models import Document, Page

pytestmark = pytest.mark.integration

def test_migration_seed_import_and_scope(database, tmp_path):
    seed_catalog(database)
    seed_catalog(database)
    pdf = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(pdf)
    metadata = dict(equipment_id="brother_dcp_t430w", title="Blank extraction fixture",
        language="es", edition="test", applicability_note="Not a technical source")
    first = import_pdf(database, pdf, metadata, tmp_path)
    assert import_pdf(database, pdf, metadata, tmp_path).id == first.id
    assert database.scalar(select(func.count()).select_from(Document)) == 1
    page = database.scalar(select(Page))
    assert not page.approved and page.extraction_status == "empty" and page.page_number == 1
    assert catalog_rows(database, "human_resources") == []
    assert len(catalog_rows(database, "office_printer_maintenance")) == 1
    metadata["reviewed_document_type"] = "driver_guide"
    reviewed = import_pdf(database, pdf, metadata, tmp_path)
    database.flush()
    assert reviewed.document_type == "driver_guide" and reviewed.classification_reviewed
    assert not page.approved  # Classification review does not authorize technical answers.
    database.commit()

def test_unknown_equipment_cannot_import(database, tmp_path):
    with pytest.raises(ValueError, match="Unknown equipment"):
        import_pdf(database, tmp_path / "not-read.pdf", {"equipment_id": "other"}, tmp_path)
