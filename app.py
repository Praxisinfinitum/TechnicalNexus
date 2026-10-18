"""Phase-1 catalog, intentionally not a chatbot."""
import streamlit as st
from sqlalchemy.orm import Session
from technicalnexus.config import Settings
from technicalnexus.database import engine_for
from technicalnexus.documents import catalog_rows
from technicalnexus.i18n import translate as t
from technicalnexus.scope import INSTANCE_ID

st.set_page_config(page_title="TechnicalNexus", page_icon="📚", layout="wide")
st.title(t("title"))
st.caption(t("subtitle"))
st.subheader(t("phase"))
st.info(t("notice"))
st.selectbox(t("equipment"), ["Brother DCP-T430W"])
st.caption(t("pending"))
st.write(t("scope"))
st.subheader(t("sources"))
engine = None
try:
    engine = engine_for(Settings.load().database_url)
    with Session(engine) as session:
        rows = catalog_rows(session, INSTANCE_ID)
    st.success(t("db_ok"))
    if rows:
        st.dataframe([{t(k): t("type_" + v) if k == "type" else v for k, v in row.items()} for row in rows], hide_index=True, width="stretch")
        st.caption(t("review"))
    else:
        st.info(t("empty"))
except Exception:
    # Never display connection strings, credentials or driver tracebacks in the GUI.
    st.error(t("db_error"))
finally:
    if engine is not None:
        engine.dispose()
