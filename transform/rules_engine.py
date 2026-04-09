# =========================
# CONFIGURACIÓN
# =========================

SYSTEM_TABLES = {
    "sysdiagrams",
    "dtproperties"
}

FORCE_EXCLUDE = set()
FORCE_INCLUDE = set()

# reglas por tipo
TYPE_RULES = {
    "CORE": "INCLUDE",
    "TRANSACCIONAL": "INCLUDE",
    "CATALOGO": "EXCLUDE",
    "SOPORTE": "EXCLUDE"
}


def decidir(tabla, tipo):
    """
    Decide si una tabla entra en el proceso ETL
    """

    # 🔴 Overrides manuales
    if tabla in FORCE_EXCLUDE:
        return "EXCLUDE"

    if tabla in FORCE_INCLUDE:
        return "INCLUDE"

    # ⚙️ Sistema
    if tabla in SYSTEM_TABLES:
        return "EXCLUDE"

    # 📊 Regla por tipo
    return TYPE_RULES.get(tipo, "EXCLUDE")