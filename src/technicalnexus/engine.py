"""Deterministic, conservative Spanish rules. NLTK tokenization needs no download."""
import re
import unicodedata
from typing import Protocol
from nltk.tokenize import RegexpTokenizer
from technicalnexus.contracts import ConversationContext, EngineResponse, QueryRequest, ResponseStatus
from technicalnexus.i18n import translate
from technicalnexus.knowledge import ReviewedAnswer
from technicalnexus.scope import EQUIPMENT, EQUIPMENT_LABELS, INSTANCE_ID, KNOWN_EQUIPMENT, select_equipment

TOKENIZER = RegexpTokenizer(r"[a-z]+|\d+")
SUPPORTED_MODELS = {
    "brother_dcp_t430w": re.compile(r"\b(?:dcp )?t 430 w\b"),
    "brother_dcp_t220": re.compile(r"\b(?:dcp )?t 220\b(?! [a-z]\b)"),
    "canon_c3935i": re.compile(r"\bc 3935 i\b"),
}
OTHER_MODEL = re.compile(r"\b(?:dcp|mfc|hl|t|l|g|c|laserjet|deskjet|pixma) (?:[a-z] )?\d+(?: [a-z]+)?\b")

class AnswerRepository(Protocol):
    def find(self, instance_id: str, equipment_id: str, intent_id: str, language: str) -> ReviewedAnswer | None: ...

def normalize_query(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(TOKENIZER.tokenize(plain))

def matches(pattern: str, text: str) -> bool:
    return re.search(pattern, text) is not None

def technical_intents(text: str) -> list[str]:
    found = []
    rules = [
        ("ink_level", r"\b(?:nivel|niveles|volumen|cantidad|poca|baja)\b.*\btinta\b|\btinta\b.*\b(?:nivel|volumen|baja)\b|\bcuando\b.*\brellen\w*\b"),
        ("after_refill", r"\b(?:ya|despues|tras)\b.*\b(?:rellen\w*|recarg\w*)\b|\b(?:rellene|recargue)\b|\bled\b.*\btinta\b"),
        ("no_paper", r"\b(?:no hay|sin|falta|cargar) papel\b|\bpapel no cargado\b"),
        ("tray_not_detected", r"\bbandeja\b.*\b(?:no|sin)\b.*\bdetect\w*\b|\bno detect\w*\b.*\bbandeja\b"),
        ("print_quality", r"\bcalidad (?:de )?(?:la )?impresion\b|\b(?:rayas|bandas|lineas)\b.*\b(?:impresion|impresa|impresas|imprimir)\b|\b(?:imprime|impresion|hoja|paginas)\b.*\b(?:rayas|bandas|lineas)\b|\b(?:limpiar|limpieza)\b.*\bcabezal(?:es)?\b"),
        ("paper_jam", r"\b(?:atasco|atascado|atascada|atorado|atorada)\b"),
        ("manual_location", r"\b(?:manual|manuales|documentacion|guia del usuario)\b"),
        ("toner_level", r"\b(?:nivel|niveles|cantidad|restante|queda|poco|bajo)\b.*\btoner\b|\btoner\b.*\b(?:nivel|niveles|cantidad|restante|queda|bajo)\b"),
        ("glass_cleaning", r"\b(?:limpiar|limpieza)\b.*\b(?:cristal|escaner)\b"),
    ]
    for intent, pattern in rules:
        if matches(pattern, text):
            found.append(intent)
    # An ink warning after a completed refill is more specific than checking volume.
    if "after_refill" in found and "ink_level" in found:
        found.remove("ink_level")
    return found

class RulesEngine:
    def __init__(self, repository: AnswerRepository):
        self.repository = repository

    def respond(self, request: QueryRequest) -> EngineResponse:
        context = request.context
        def result(status, intent, message, ctx=None, refs=()):
            return EngineResponse(status, intent, translate(message), ctx or context, refs)
        if request.language != "es":
            return result(ResponseStatus.ERROR, "unsupported_language", "engine_language")
        if context.instance_id != INSTANCE_ID:
            return result(ResponseStatus.OUT_OF_SCOPE, "outside_scope", "engine_scope", ConversationContext())
        if context.equipment_id is not None and context.equipment_id not in KNOWN_EQUIPMENT:
            return result(ResponseStatus.OUT_OF_SCOPE, "unsupported_equipment", "engine_unknown_model", ConversationContext())
        if len(request.text) > 2000:
            return result(ResponseStatus.CLARIFICATION, "clarification", "engine_long")
        text = normalize_query(request.text)
        if not text:
            return result(ResponseStatus.CLARIFICATION, "clarification", "engine_empty")

        # Scope restrictions precede intent and device selection, even in mixed queries.
        if matches(r"\b(?:nom|iso|norma|normas|normativ\w*|reglamento\w*|legislacion|ley|leyes)\b", text):
            return result(ResponseStatus.NO_EVIDENCE, "unavailable_regulation", "engine_norm")
        if matches(r"\b(?:nomina|salario\w*|reclut\w*|contratacion|vacaciones|recursos humanos|rr hh|hospital\w*|medico\w*|automovil\w*)\b", text):
            return result(ResponseStatus.OUT_OF_SCOPE, "outside_scope", "engine_scope")
        # Do not turn requests to bypass sources into answers about a detected keyword.
        if matches(r"\b(?:ignora\w*|inventa\w*|omite\w*)\b|\bsin (?:manual\w*|documentacion|fuentes|restricciones)\b", text):
            return result(ResponseStatus.OUT_OF_SCOPE, "outside_scope", "engine_sources")
        if matches(r"\b(?:desmont\w*|desarm\w*|repar\w*|fusor|voltaje|electronic\w*|alcohol|solvente\w*|acetona|limpieza especial)\b", text):
            return result(ResponseStatus.NO_EVIDENCE, "service_escalation", "engine_service")

        selected = [key for key, pattern in SUPPORTED_MODELS.items() if pattern.search(text)]
        without_supported = text
        for pattern in SUPPORTED_MODELS.values():
            without_supported = pattern.sub("", without_supported)
        unknown_model = OTHER_MODEL.search(without_supported)
        other_brand = matches(r"\b(?:hp|epson|xerox|lexmark|samsung|ricoh)\b", text)
        brands = {brand for brand in ("brother", "canon") if matches(r"\b" + brand + r"\b", text)}
        if (unknown_model or other_brand or len(selected) > 1 or len(brands) > 1
                or (selected and brands and EQUIPMENT[selected[0]][0].casefold() not in brands)):
            return result(ResponseStatus.OUT_OF_SCOPE, "unsupported_equipment", "engine_unknown_model", ConversationContext())
        supported = bool(selected)
        if not supported and brands and (context.equipment_id is None
                or EQUIPMENT[context.equipment_id][0].casefold() not in brands):
            return result(ResponseStatus.CLARIFICATION, "select_equipment", "engine_select", ConversationContext())
        if text in {"adios", "salir", "hasta luego", "terminar", "cerrar"}:
            return result(ResponseStatus.ANSWER, "goodbye", "engine_goodbye", ConversationContext())
        if text in {"reiniciar", "reiniciar conversacion", "nuevo caso", "reset"}:
            return result(ResponseStatus.ANSWER, "reset", "engine_reset", ConversationContext())
        if text in {"cambiar impresora", "cambiar equipo", "otra impresora", "seleccionar impresora"}:
            return result(ResponseStatus.CLARIFICATION, "select_equipment", "engine_select", ConversationContext())
        if text in {"hola", "buenos dias", "buenas tardes", "buenas noches"}:
            return result(ResponseStatus.ANSWER, "greeting", "engine_greeting")
        if text in {"ayuda", "opciones", "que puedes hacer", "que puedo preguntar"}:
            return result(ResponseStatus.ANSWER, "help", "engine_help")

        if supported:
            # A fresh explicit model selection resets pending technical state; a reply
            # to a model clarification can resume exactly one remembered intent.
            previous_pending = context.pending_fields
            previous_equipment = context.equipment_id
            context = select_equipment(context, selected[0])
            if previous_equipment is not None:
                previous_pending = ()  # Never carry a pending intent across model switches.
        else:
            previous_pending = ()
        intents = technical_intents(text)
        if len(intents) > 1:
            return result(ResponseStatus.CLARIFICATION, "clarification", "engine_multiple",
                ConversationContext(equipment_id=context.equipment_id))
        if not intents and supported and len(previous_pending) == 1 and previous_pending[0].startswith("intent:"):
            intents = [previous_pending[0].split(":", 1)[1]]
        if not intents:
            if supported:
                return EngineResponse(ResponseStatus.ANSWER, "select_equipment",
                    translate("engine_selected").format(model=EQUIPMENT_LABELS[context.equipment_id]), context)
            if "brother" in text or matches(r"\b(?:mantenimiento|impresora|tinta|papel)\b", text):
                return result(ResponseStatus.CLARIFICATION, "clarification", "engine_detail", context)
            return result(ResponseStatus.NO_EVIDENCE, "no_evidence", "engine_no_evidence", context)

        intent = intents[0]
        if context.equipment_id is None:
            return result(ResponseStatus.CLARIFICATION, "select_equipment", "engine_select",
                ConversationContext(pending_fields=("intent:" + intent,)))
        # Negated symptoms and unsupported qualifiers must not trigger affirmative advice.
        if matches(r"\b(?:no tengo|no hay|sin) (?:atasco\w*|rayas|bandas)\b|\bno (?:quiero|necesito|limpiar|rellenar)\b", text):
            return result(ResponseStatus.CLARIFICATION, "clarification", "engine_detail", context)
        if intent == "no_paper" and matches(r"\b(?:si hay papel|tiene papel|llena)\b", text):
            return result(ResponseStatus.CLARIFICATION, "clarification", "engine_detail", context)
        if matches(r"\b(?:precio|costo|coste|comprar|garantia|frecuencia|cada cuanto|codigo|error \d+|modelo)\b", without_supported):
            return result(ResponseStatus.NO_EVIDENCE, "no_evidence", "engine_no_evidence", context)
        try:
            answer = self.repository.find(context.instance_id, context.equipment_id, intent, request.language)
        except Exception:
            return result(ResponseStatus.ERROR, "technical_error", "engine_error", context)
        if answer is None or not answer.references:
            return result(ResponseStatus.NO_EVIDENCE, "no_evidence", "engine_no_evidence", context)
        body = answer.text
        if answer.conditions:
            body += "\n\n" + translate("engine_conditions") + " " + answer.conditions
        return EngineResponse(ResponseStatus.ANSWER, intent, body, context, answer.references)
