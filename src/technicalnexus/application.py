"""Application service reusable by Streamlit and a future HTTP adapter."""
from sqlalchemy.orm import Session
from technicalnexus.config import Settings
from technicalnexus.contracts import EngineResponse, QueryRequest, ResponseStatus
from technicalnexus.database import engine_for
from technicalnexus.engine import RulesEngine
from technicalnexus.i18n import translate
from technicalnexus.knowledge import KnowledgeRepository

def respond_to_query(request: QueryRequest) -> EngineResponse:
    engine = None
    try:
        engine = engine_for(Settings.load().database_url)
        with Session(engine) as session:
            return RulesEngine(KnowledgeRepository(session)).respond(request)
    except Exception:
        return EngineResponse(ResponseStatus.ERROR, "technical_error", translate("engine_error"), request.context)
    finally:
        if engine is not None:
            engine.dispose()
