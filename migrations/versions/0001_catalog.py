"""Initial catalog schema. Immutable SQL snapshot, PostgreSQL only."""
from alembic import op
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute('\nCREATE TABLE documents (\n\tid VARCHAR(64) NOT NULL, \n\toriginal_filename VARCHAR(255) NOT NULL, \n\trelative_path TEXT NOT NULL, \n\ttitle TEXT NOT NULL, \n\tdocument_type VARCHAR(80) NOT NULL, \n\tlanguage VARCHAR(30) NOT NULL, \n\tedition VARCHAR(100) NOT NULL, \n\tsource_url TEXT, \n\tprovenance TEXT NOT NULL, \n\tpage_count INTEGER NOT NULL, \n\tclassification_reviewed BOOLEAN NOT NULL, \n\tPRIMARY KEY (id), \n\tCHECK (page_count > 0)\n)\n\n')
    op.execute('\nCREATE TABLE instances (\n\tid VARCHAR(100) NOT NULL, \n\tname VARCHAR(200) NOT NULL, \n\tPRIMARY KEY (id)\n)\n\n')
    op.execute('\nCREATE TABLE document_pages (\n\tid SERIAL NOT NULL, \n\tdocument_id VARCHAR(64) NOT NULL, \n\tpage_number INTEGER NOT NULL, \n\traw_text TEXT NOT NULL, \n\tnormalized_text TEXT NOT NULL, \n\textraction_status VARCHAR(30) NOT NULL, \n\tapproved BOOLEAN NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (document_id, page_number), \n\tCHECK (page_number > 0), \n\tFOREIGN KEY(document_id) REFERENCES documents (id)\n)\n\n')
    op.execute('\nCREATE TABLE equipment (\n\tid VARCHAR(100) NOT NULL, \n\tinstance_id VARCHAR(100) NOT NULL, \n\tbrand VARCHAR(100) NOT NULL, \n\tmodel VARCHAR(100) NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(instance_id) REFERENCES instances (id)\n)\n\n')
    op.execute('\nCREATE TABLE intents (\n\tid VARCHAR(100) NOT NULL, \n\tinstance_id VARCHAR(100) NOT NULL, \n\tdescription TEXT NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(instance_id) REFERENCES instances (id)\n)\n\n')
    op.execute('\nCREATE TABLE answers (\n\tid SERIAL NOT NULL, \n\tequipment_id VARCHAR(100) NOT NULL, \n\tintent_id VARCHAR(100) NOT NULL, \n\tlanguage VARCHAR(10) NOT NULL, \n\ttext TEXT NOT NULL, \n\tapproved BOOLEAN NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(equipment_id) REFERENCES equipment (id), \n\tFOREIGN KEY(intent_id) REFERENCES intents (id)\n)\n\n')
    op.execute("\nCREATE TABLE document_equipment (\n\tdocument_id VARCHAR(64) NOT NULL, \n\tequipment_id VARCHAR(100) NOT NULL, \n\tstatus VARCHAR(30) NOT NULL, \n\tevidence TEXT NOT NULL, \n\tPRIMARY KEY (document_id, equipment_id), \n\tCHECK (status IN ('pending', 'confirmed', 'excluded')), \n\tFOREIGN KEY(document_id) REFERENCES documents (id), \n\tFOREIGN KEY(equipment_id) REFERENCES equipment (id)\n)\n\n")
    op.execute('\nCREATE TABLE answer_sources (\n\tanswer_id INTEGER NOT NULL, \n\tpage_id INTEGER NOT NULL, \n\tPRIMARY KEY (answer_id, page_id), \n\tFOREIGN KEY(answer_id) REFERENCES answers (id), \n\tFOREIGN KEY(page_id) REFERENCES document_pages (id)\n)\n\n')

def downgrade():
    op.execute("DROP TABLE answer_sources")
    op.execute("DROP TABLE document_equipment")
    op.execute("DROP TABLE answers")
    op.execute("DROP TABLE intents")
    op.execute("DROP TABLE equipment")
    op.execute("DROP TABLE document_pages")
    op.execute("DROP TABLE instances")
    op.execute("DROP TABLE documents")
