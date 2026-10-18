from streamlit.testing.v1 import AppTest
from technicalnexus.config import ROOT

def test_spanish_catalog_starts():
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)
    assert not app.exception
    assert app.title[0].value == "TechnicalNexus"
    assert app.selectbox[0].value == "Brother DCP-T430W"
    assert "fase 2" in app.info[0].value
    assert not app.error
    assert "PostgreSQL" in app.success[0].value

def test_connection_failure_is_explained_without_credentials(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://hidden_user:hidden_password@127.0.0.1:1/no_database")
    app = AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)
    assert not app.exception
    assert "PostgreSQL" in app.error[0].value
    assert "hidden_password" not in app.error[0].value
