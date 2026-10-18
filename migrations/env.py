from alembic import context
from technicalnexus.config import Settings
from technicalnexus.database import engine_for
from technicalnexus.models import Base

def run():
    with engine_for(Settings.load().database_url).connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()

run()
