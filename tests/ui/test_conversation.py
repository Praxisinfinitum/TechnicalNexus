import os
from streamlit.testing.v1 import AppTest
from technicalnexus.config import ROOT

def app():
    return AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)

def send(ui, message):
    ui.chat_input[0].set_value(message).run(timeout=20)
    assert not ui.exception
    return ui.session_state["conversation"]

def test_pending_question_selection_reference_and_reset(reviewed_ink_database):
    ui = app()
    state = send(ui, "Nivel de tinta")
    assert state.context.equipment_id is None and state.messages[-1].status == "clarification"
    ui.selectbox[0].set_value("brother_dcp_t430w").run(timeout=20)
    assert not ui.exception
    state = ui.session_state["conversation"]
    assert state.messages[-1].references[0].filename == "reviewed-fixture.pdf"
    assert any("Fuente:" in label.value and "pág. 1" in label.value for label in ui.caption)
    ui.run(timeout=20)
    assert ui.session_state["conversation"] == state  # Ordinary reruns do not duplicate messages.
    ui.button(key="reset_chat").click().run(timeout=20)
    assert not ui.exception
    assert ui.selectbox[0].value is None
    assert not ui.session_state["conversation"].messages

def test_typed_model_rejection_and_selector_stay_synchronized(reviewed_ink_database):
    ui = app()
    send(ui, "DCP-T430W")
    assert ui.selectbox[0].value == "brother_dcp_t430w"
    state = send(ui, "Epson L3250")
    assert state.context.equipment_id is None and ui.selectbox[0].value is None
    state = send(ui, "Nivel de tinta")
    assert state.messages[-1].status == "clarification"
    state = send(ui, "DCP-T430W")
    assert state.messages[-1].references and ui.selectbox[0].value == "brother_dcp_t430w"

def test_two_browser_sessions_do_not_share_history_or_model(reviewed_ink_database):
    first, second = app(), app()
    send(first, "DCP-T430W")
    send(first, "Nivel de tinta")
    assert second.session_state["conversation"].context.equipment_id is None
    assert not second.session_state["conversation"].messages
    state = send(second, "Nivel de tinta")
    assert state.messages[-1].status == "clarification"
    assert first.session_state["conversation"].messages[-1].references

def test_data_failure_keeps_history_and_can_recover(reviewed_ink_database, monkeypatch):
    ui = app()
    send(ui, "DCP-T430W")
    working_url = os.environ["DATABASE_URL"]
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://hidden_user:hidden_password@127.0.0.1:1/missing")
    state = send(ui, "Nivel de tinta")
    assert state.messages[-1].status == "error" and not state.messages[-1].references
    assert state.context.equipment_id == "brother_dcp_t430w"
    assert all("hidden_password" not in message.text for message in state.messages)
    monkeypatch.setenv("DATABASE_URL", working_url)
    state = send(ui, "Nivel de tinta")
    assert state.messages[-1].references
