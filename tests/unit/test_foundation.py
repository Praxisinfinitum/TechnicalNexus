import pytest
from technicalnexus.config import Settings
from technicalnexus.contracts import ConversationContext, ResponseStatus
from technicalnexus.documents import classify_document, normalize_text
from technicalnexus.i18n import translate
from technicalnexus.scope import select_equipment

def test_configuration_requires_postgresql_and_supported_language():
    with pytest.raises(ValueError): Settings("sqlite:///app.db")
    with pytest.raises(ValueError): Settings("postgresql+psycopg://localhost/app", "fr")
    assert Settings("postgresql+psycopg://localhost/app").language == "es"

def test_normalization_preserves_warning_negation_and_lines():
    assert normalize_text("  ADVERTENCIA\r\n No  toque\t el cabezal. ") == "ADVERTENCIA\nNo toque el cabezal."
    assert normalize_text("\n \t") == ""

@pytest.mark.parametrize(("text", "kind"), [("Guía de consulta", "reference"),
    ("Open Source Licensing Remarks", "licensing"), ("Unknown", "unclassified")])
def test_classification_is_conservative(text, kind):
    assert classify_document(text) == kind

def test_message_fallback_and_contract_codes():
    assert translate("equipment", "fr") == "Equipo disponible"
    assert translate("unknown") == "Texto no disponible"
    assert ResponseStatus.NO_EVIDENCE.value == "no_evidence"

def test_selection_does_not_mutate_previous_context():
    old = ConversationContext(pending_fields=("symptom",))
    new = select_equipment(old, "brother_dcp_t430w")
    assert old.equipment_id is None and old.pending_fields == ("symptom",)
    assert new.pending_fields == ()
