"""Spanish presentation catalog; message IDs are language-independent."""
CATALOGS = {"es": {
    "title": "TechnicalNexus",
    "subtitle": "Asistencia técnica con documentación autorizada",
    "phase": "Fase 1 · Base del proyecto",
    "notice": "Esta versión muestra el catálogo documental. El chatbot se implementará en la fase 2.",
    "equipment": "Equipo disponible",
    "pending": "Los otros dos modelos están pendientes de selección.",
    "db_ok": "Conexión con PostgreSQL verificada.",
    "db_error": "No se pudo consultar PostgreSQL. Revisa la configuración y ejecuta la preparación indicada en README.",
    "empty": "Aún no hay documentos importados. Ejecuta la importación indicada en README.",
    "sources": "Documentos registrados (no autorizados automáticamente para respuestas)",
    "model": "Modelo", "file": "Archivo", "document": "Documento", "pages": "Páginas",
    "type": "Tipo propuesto", "review": "Revisión pendiente", "missing": "Texto no disponible",
    "type_reference": "Consulta", "type_quick_setup": "Configuración rápida",
    "type_product_safety": "Seguridad del producto", "type_network_security": "Seguridad de red",
    "type_licensing": "Licencias", "type_software_guide": "Guía de software",
    "type_driver_guide": "Controlador", "type_wifi_channels": "Canales Wi-Fi",
    "type_unclassified": "Sin clasificar",
    "scope": "Ámbito: mantenimiento de impresoras de oficina. Sin diagnóstico automático ni acciones sobre equipos.",
}}

def translate(key: str, language: str = "es") -> str:
    return CATALOGS.get(language, CATALOGS["es"]).get(key, CATALOGS["es"]["missing"])
