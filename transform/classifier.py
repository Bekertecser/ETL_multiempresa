def es_catalogo(tabla, columnas, fk_count, referenced_by):
    patrones = ["tipo", "estado", "catalogo", "parametro", "maestro"]

    nombre_match = any(p in tabla.lower() for p in patrones)
    pocas_columnas = len(columnas) <= 6
    poco_referenciada = referenced_by.get(tabla, 0) < 5

    return nombre_match and pocas_columnas and poco_referenciada


def es_transaccional(columnas):
    claves = ["fecha", "valor", "total", "cantidad"]

    return any(
        any(c in col["name"].lower() for c in claves)
        for col in columnas
    )


def es_core(tabla, fk_count, referenced_by):
    """
    Tablas core suelen:
    - ser referenciadas por muchas
    - tener varias FK
    """
    return referenced_by.get(tabla, 0) >= 5


def clasificar(metadata, fk_count, referenced_by):
    """
    Clasifica tablas en:
    - CATALOGO
    - TRANSACCIONAL
    - CORE
    """

    clasificacion = {}

    for tabla, data in metadata.items():
        columnas = data.get("columns", [])

        if es_catalogo(tabla, columnas, fk_count, referenced_by):
            tipo = "CATALOGO"

        elif es_core(tabla, fk_count, referenced_by):
            tipo = "CORE"

        elif es_transaccional(columnas):
            tipo = "TRANSACCIONAL"

        else:
            tipo = "SOPORTE"

        clasificacion[tabla] = tipo

    return clasificacion