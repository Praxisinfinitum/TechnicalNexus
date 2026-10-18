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

@pytest.fixture
def database(monkeypatch):
    load_dotenv(ROOT / ".env", override=False)
    raw = os.environ.get("TEST_DATABASE_URL")
    if not raw:
        pytest.fail("TEST_DATABASE_URL required; run scripts/local_postgres.py start")
    url = make_url(raw)
    development = make_url(os.environ["DATABASE_URL"])
    if not (url.database or "").endswith("_test") or (url.host, url.port, url.database) == (development.host, development.port, development.database):
        pytest.fail("Unsafe test database: use a separate *_test database")
    schema = "test_" + uuid4().hex
    engine = engine_for(raw)
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    scoped = url.update_query_dict({"options": f"-csearch_path={schema}"}).render_as_string(hide_password=False)
    monkeypatch.setenv("DATABASE_URL", scoped)
    try:
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
        scoped_engine = engine_for(scoped)
        try:
            with Session(scoped_engine) as session:
                yield session
        finally:
            scoped_engine.dispose()
    finally:
        # Only the unique schema created by this fixture, in the dedicated test DB.
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()

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
