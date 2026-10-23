from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from technicalnexus.config import Settings
from technicalnexus.models import Equipment, Instance
from technicalnexus.scope import EQUIPMENT, INSTANCE_ID

def engine_for(url: str):
    Settings(url)  # Enforce PostgreSQL, including integration tests.
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 3})

def seed_catalog(session: Session):
    session.merge(Instance(id=INSTANCE_ID, name="Office printer maintenance"))
    session.flush()
    for key, (brand, model) in EQUIPMENT.items():
        session.merge(Equipment(id=key, instance_id=INSTANCE_ID, brand=brand, model=model))
    session.flush()
