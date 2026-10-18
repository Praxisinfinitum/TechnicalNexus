import pytest
from technicalnexus.engine import technical_intents, normalize_query
from technicalnexus.guidance import OPTIONS

@pytest.mark.parametrize("option", OPTIONS, ids=lambda option: option.intent_id)
def test_guided_queries_identify_exactly_the_intended_rule(option):
    assert technical_intents(normalize_query(option.query)) == [option.intent_id]
