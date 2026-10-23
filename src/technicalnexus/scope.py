"""Equipment selection only; does not claim to classify arbitrary user text."""
from dataclasses import replace
from technicalnexus.contracts import ConversationContext

EQUIPMENT = {
    "brother_dcp_t430w": ("Brother", "DCP-T430W"),
    "brother_dcp_t220": ("Brother", "DCP-T220"),
    "canon_c3935i": ("Canon", "imageRUNNER ADVANCE DX C3935i"),
}
KNOWN_EQUIPMENT = set(EQUIPMENT)
EQUIPMENT_LABELS = {key: f"{brand} {model}" for key, (brand, model) in EQUIPMENT.items()}
INSTANCE_ID = "office_printer_maintenance"

def select_equipment(context: ConversationContext, equipment_id: str) -> ConversationContext:
    if context.instance_id != INSTANCE_ID:
        raise ValueError("Unsupported instance")
    if equipment_id not in KNOWN_EQUIPMENT:
        raise ValueError("Unsupported equipment")
    return replace(context, equipment_id=equipment_id, pending_fields=())
