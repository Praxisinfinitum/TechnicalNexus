"""Record reviewed-answer conditions and section-level references."""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("answers", sa.Column("conditions", sa.Text(), nullable=False, server_default=""))
    op.add_column("answers", sa.Column("review_note", sa.Text(), nullable=False, server_default=""))
    op.add_column("answer_sources", sa.Column("section", sa.Text(), nullable=False, server_default=""))
    op.create_unique_constraint("uq_answer_scope", "answers", ["equipment_id", "intent_id", "language"])

def downgrade():
    op.drop_constraint("uq_answer_scope", "answers", type_="unique")
    op.drop_column("answer_sources", "section")
    op.drop_column("answers", "review_note")
    op.drop_column("answers", "conditions")
