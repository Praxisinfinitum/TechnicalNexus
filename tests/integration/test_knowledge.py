import json
from hashlib import sha256
import pytest
from sqlalchemy import select
from technicalnexus.database import seed_catalog
from technicalnexus.knowledge import KnowledgeRepository, load_reviewed_knowledge
from technicalnexus.models import Answer, AnswerSource, Applicability, Document, Intent, Page
from technicalnexus.scope import INSTANCE_ID

pytestmark = pytest.mark.integration

def populate(session):
    seed_catalog(session)
    session.add(Document(id="a" * 64, original_filename="fixture.pdf", relative_path="fixture.pdf",
        title="Fixture", document_type="reference", language="es", edition="test", provenance="test", page_count=2))
    session.add(Intent(id="ink_level", instance_id=INSTANCE_ID, description="Ink"))
    session.flush()
    session.add(Applicability(document_id="a" * 64, equipment_id="brother_dcp_t430w", status="confirmed", evidence="fixture"))
    page = Page(document_id="a" * 64, page_number=1, raw_text="tinta", normalized_text="tinta", extraction_status="extracted", approved=True)
    answer = Answer(equipment_id="brother_dcp_t430w", intent_id="ink_level", language="es", text="Reviewed",
        conditions="Only the selected equipment", review_note="fixture review", approved=True)
    session.add_all([page, answer])
    session.flush()
    session.add(AnswerSource(answer_id=answer.id, page_id=page.id, section="Ink"))
    session.flush()
    return page, answer

def test_exact_scope_language_and_approval_boundaries(database):
    page, answer = populate(database)
    repository = KnowledgeRepository(database)
    assert repository.find(INSTANCE_ID, "brother_dcp_t430w", "ink_level", "es").references[0].page_number == 1
    for instance, equipment, language in [("hr", "brother_dcp_t430w", "es"),
        (INSTANCE_ID, "other", "es"), (INSTANCE_ID, "brother_dcp_t430w", "en")]:
        assert repository.find(instance, equipment, "ink_level", language) is None
    answer.approved = False
    database.flush()
    assert repository.find(INSTANCE_ID, "brother_dcp_t430w", "ink_level", "es") is None

@pytest.mark.parametrize("invalid", ["page", "applicability", "second_source", "empty_review"])
def test_every_required_source_must_be_reviewed(database, invalid):
    page, answer = populate(database)
    if invalid == "page":
        page.approved = False
    elif invalid == "applicability":
        database.get(Applicability, (page.document_id, "brother_dcp_t430w")).status = "pending"
    elif invalid == "empty_review":
        answer.review_note = ""
    else:
        second = Page(document_id=page.document_id, page_number=2, raw_text="raw", normalized_text="raw",
            extraction_status="extracted", approved=False)
        database.add(second)
        database.flush()
        database.add(AnswerSource(answer_id=answer.id, page_id=second.id, section="Unreviewed"))
    database.flush()
    assert KnowledgeRepository(database).find(INSTANCE_ID, "brother_dcp_t430w", "ink_level", "es") is None

def test_review_manifest_is_repeatable_and_detects_changed_original(database, tmp_path):
    seed_catalog(database)
    original = tmp_path / "review-fixture.pdf"
    original.write_bytes(b"source-version-fixture")
    digest = sha256(original.read_bytes()).hexdigest()
    database.add(Document(id=digest, original_filename=original.name, relative_path=original.name,
        title="Fixture", document_type="reference", language="es", edition="fixture", provenance="test", page_count=1))
    database.flush()
    database.add(Applicability(document_id=digest, equipment_id="brother_dcp_t430w", status="pending", evidence="test"))
    database.add(Page(document_id=digest, page_number=1, raw_text="nivel de tinta", normalized_text="nivel de tinta",
        extraction_status="extracted", approved=False))
    database.flush()
    payload = {"instance_id": INSTANCE_ID, "equipment_id": "brother_dcp_t430w", "review_note": "explicit fixture review",
        "applicability_review": "fixture", "answers": [{"intent_id": "ink_level", "description": "Ink",
        "text": "Reviewed fixture", "conditions": "Fixture only", "sources": [{"sha256": digest,
        "filename": original.name, "page": 1, "section": "Ink", "anchors": ["tinta"]}]}]}
    manifest = tmp_path / "review.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    load_reviewed_knowledge(database, manifest, tmp_path)
    load_reviewed_knowledge(database, manifest, tmp_path)
    assert len(list(database.scalars(select(Answer)))) == 1
    assert len(list(database.scalars(select(AnswerSource)))) == 1
    assert KnowledgeRepository(database).find(INSTANCE_ID, "brother_dcp_t430w", "ink_level", "es") is not None
    original.write_bytes(b"different-source-version")
    with pytest.raises(ValueError, match="differs"):
        load_reviewed_knowledge(database, manifest, tmp_path)


def test_model_specific_lookup_and_revocation_do_not_affect_other_models(reviewed_multi_database):
    session = reviewed_multi_database
    repo = KnowledgeRepository(session)
    assert repo.find(INSTANCE_ID, "brother_dcp_t220", "ink_level", "es").text == "T220 ink"
    assert repo.find(INSTANCE_ID, "canon_c3935i", "ink_level", "es") is None
    assert repo.find(INSTANCE_ID, "brother_dcp_t220", "toner_level", "es") is None
    scope = session.get(Applicability, ("d"*64, "brother_dcp_t220"))
    scope.status = "excluded"
    session.flush()
    assert repo.find(INSTANCE_ID, "brother_dcp_t220", "ink_level", "es") is None
    assert repo.find(INSTANCE_ID, "brother_dcp_t430w", "ink_level", "es") is not None
    assert repo.find(INSTANCE_ID, "canon_c3935i", "toner_level", "es") is not None
