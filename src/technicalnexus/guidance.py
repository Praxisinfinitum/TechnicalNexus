"""Curated navigation labels and canonical queries, never a second answer store."""
from dataclasses import dataclass
from technicalnexus.contracts import ConversationContext
from technicalnexus.knowledge import KnowledgeRepository

@dataclass(frozen=True)
class GuidedOption:
    intent_id: str
    topic: str
    label: str
    query: str

OPTIONS = (
    GuidedOption("ink_level", "ink", "guide_ink_level", "Nivel de tinta"),
    GuidedOption("after_refill", "ink", "guide_after_refill", "Ya rellené la tinta"),
    GuidedOption("no_paper", "paper", "guide_no_paper", "No hay papel"),
    GuidedOption("tray_not_detected", "paper", "guide_tray", "Bandeja no detectada"),
    GuidedOption("paper_jam", "paper", "guide_jam", "Atasco de papel"),
    GuidedOption("print_quality", "quality", "guide_cleaning", "Limpieza normal del cabezal"),
    GuidedOption("manual_location", "documents", "guide_manual", "Dónde consultar el manual"),
)

def available_options(repository: KnowledgeRepository, context: ConversationContext):
    """Apply exactly the runtime approval/source gates for this model and instance."""
    if context.equipment_id is None:
        return ()
    return tuple(option for option in OPTIONS if repository.find(
        context.instance_id, context.equipment_id, option.intent_id, "es") is not None)
