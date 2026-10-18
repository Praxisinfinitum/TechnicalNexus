from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from technicalnexus.config import Settings
from technicalnexus.models import Equipment, Instance
from technicalnexus.scope import INSTANCE_ID

def engine_for(url: str):
    Settings(url)  # Enforce PostgreSQL, including integration tests.
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 3})

def seed_catalog(session: Session):
    session.merge(Instance(id=INSTANCE_ID, name="Office printer maintenance"))
    session.flush()
    session.merge(Equipment(id="brother_dcp_t430w", instance_id=INSTANCE_ID, brand="Brother", model="DCP-T430W"))
    session.flush()
