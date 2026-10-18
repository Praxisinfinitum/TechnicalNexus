"""Spanish Streamlit conversation adapter for the scoped rules engine."""
import streamlit as st
from sqlalchemy.orm import Session
from technicalnexus.application import respond_to_query
from technicalnexus.chat import ChatState, EQUIPMENT_LABELS, choose_equipment, submit_message
from technicalnexus.config import Settings
from technicalnexus.database import engine_for
from technicalnexus.documents import catalog_rows
from technicalnexus.i18n import translate as t
from technicalnexus.scope import INSTANCE_ID

st.set_page_config(page_title="TechnicalNexus", page_icon="📚", layout="wide")

def reset_chat():
    st.session_state["conversation"] = ChatState()
    st.session_state["equipment_choice"] = None
    st.session_state["flash"] = t("ui_reset_done")

def change_equipment():
    st.session_state["conversation"] = choose_equipment(st.session_state["conversation"],
        st.session_state["equipment_choice"], respond_to_query)

state = st.session_state.setdefault("conversation", ChatState())
# Sync typed model changes before widget creation, never after it in the same run.
st.session_state["equipment_choice"] = state.context.equipment_id

st.title(t("title"))
st.caption(t("subtitle"))
st.caption(t("phase"))
st.info(t("notice"))
selection, reset = st.columns([4, 1], vertical_alignment="bottom")
with selection:
    st.selectbox(t("equipment"), [None, *EQUIPMENT_LABELS], key="equipment_choice",
        format_func=lambda value: EQUIPMENT_LABELS.get(value, t("ui_no_equipment")), on_change=change_equipment)
with reset:
    st.button(t("ui_reset"), key="reset_chat", on_click=reset_chat, width="stretch")
st.caption(t("pending"))
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

engine = None
rows = []
try:
    engine = engine_for(Settings.load().database_url)
    with Session(engine) as session:
        rows = catalog_rows(session, INSTANCE_ID)
    st.success(t("db_ok"))
except Exception:
    st.error(t("db_error"))
finally:
    if engine is not None:
        engine.dispose()

st.subheader(t("ui_chat_title"))
if not state.messages:
    st.write(t("ui_welcome"))
for message in state.messages:
    with st.chat_message(message.role):
        if message.status == "error":
            st.error(message.text)
        else:
            st.write(message.text)
        for reference in message.references:
            st.caption(t("ui_reference").format(filename=reference.filename,
                page=reference.page_number, section=reference.section))

with st.expander(t("sources"), expanded=False):
    st.caption(t("scope"))
    if rows:
        st.dataframe([{t(k): t("type_" + v) if k == "type" else v for k, v in row.items()} for row in rows],
            hide_index=True, width="stretch")
        st.caption(t("review"))
    else:
        st.info(t("empty"))
st.caption(t("ui_session_notice"))

if prompt := st.chat_input(t("ui_prompt"), max_chars=2000, key="chat_prompt"):
    with st.spinner(t("ui_working")):
        st.session_state["conversation"] = submit_message(state, prompt, respond_to_query)
    st.rerun()
