import os
from uuid import uuid4
import pytest
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from technicalnexus.config import ROOT
from technicalnexus.database import engine_for

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

@pytest.fixture
def reviewed_ink_database(database):
    """Synthetic reviewed source, so UI tests do not require private PDF originals."""
    from technicalnexus.database import seed_catalog
    from technicalnexus.models import Answer, AnswerSource, Applicability, Document, Intent, Page
    seed_catalog(database)
    database.add(Document(id="c" * 64, original_filename="reviewed-fixture.pdf", relative_path="fixture.pdf",
        title="Reviewed UI fixture", document_type="reference", language="es", edition="test",
        provenance="Synthetic test data, not manufacturer guidance", page_count=1))
    database.add(Intent(id="ink_level", instance_id="office_printer_maintenance", description="Ink level fixture"))
    database.flush()
    database.add(Applicability(document_id="c" * 64, equipment_id="brother_dcp_t430w",
        status="confirmed", evidence="Test fixture"))
    page = Page(document_id="c" * 64, page_number=1, raw_text="tinta", normalized_text="tinta",
        extraction_status="extracted", approved=True)
    answer = Answer(equipment_id="brother_dcp_t430w", intent_id="ink_level", language="es",
        text="Respuesta de tinta revisada para pruebas.", conditions="Datos sintéticos de prueba.",
        review_note="Explicit synthetic fixture review", approved=True)
    database.add_all([page, answer])
    database.flush()
    database.add(AnswerSource(answer_id=answer.id, page_id=page.id, section="Volumen de tinta"))
    database.commit()
    return database
