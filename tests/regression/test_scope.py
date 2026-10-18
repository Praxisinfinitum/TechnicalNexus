import pytest
from technicalnexus.contracts import ConversationContext
from technicalnexus.scope import select_equipment

@pytest.mark.parametrize("instance,equipment,accepted", [
    ("office_printer_maintenance", "brother_dcp_t430w", True),
    ("office_printer_maintenance", "unknown_printer", False),
    ("human_resources", "brother_dcp_t430w", False),
])
def test_equipment_scope_contract(instance, equipment, accepted):
    context = ConversationContext(instance_id=instance)
    if accepted:
        assert select_equipment(context, equipment).equipment_id == equipment
    else:
        with pytest.raises(ValueError): select_equipment(context, equipment)

# Free-text scope classification belongs to phase 2, not this selection test.
