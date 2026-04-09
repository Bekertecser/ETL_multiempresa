import pandas as pd


def clasificar_empresa_id(columnas):
    """
    Evalúa el estado de empresa_id en la tabla
    """
    empresa_col = next(
        (col for col in columnas if col["name"].lower() == "empresa_id"),
        None
    )

    if not empresa_col:
        return "SIN_EMPRESA_ID", None, False

    tipo = str(empresa_col["type"]).lower()

    if "uniqueidentifier" in tipo:
        return "OK", tipo, True

    if "bigint" in tipo:
        return "ERROR_TIPO_EMPRESA_ID", tipo, True

    return "TIPO_DESCONOCIDO", tipo, True


def generar_sql(row):
    tabla = row["tabla"]
    clas = row["clasificacion"]
    decision = row["decision"]

    # =========================
    # CASO 1: TABLAS QUE DEBEN TENER EMPRESA_ID
    # =========================
    if decision == "INCLUDE":

        # ➕ No tiene columna → agregar
        if clas == "SIN_EMPRESA_ID":
            return f"""
-- ADD empresa_id (tabla incluida en modelo multiempresa)
ALTER TABLE {tabla}
ADD empresa_id UNIQUEIDENTIFIER NULL;
""".strip()

        # 🔄 Tiene columna pero mal tipo → corregir
        if clas == "ERROR_TIPO_EMPRESA_ID":
            return f"""
-- FIX empresa_id tipo incorrecto
ALTER TABLE {tabla}
ALTER COLUMN empresa_id UNIQUEIDENTIFIER;
""".strip()

        # ✔ Ya está correcto
        return None

    # =========================
    # CASO 2: ERROR aunque no esté en INCLUDE
    # =========================
    if clas == "ERROR_TIPO_EMPRESA_ID":
        return f"""
-- FIX empresa_id tipo incorrecto (fuera de INCLUDE pero inconsistente)
ALTER TABLE {tabla}
ALTER COLUMN empresa_id UNIQUEIDENTIFIER;
""".strip()

    return None


def exportar(metadata, decisiones, clasificacion_tablas):
    data = []

    for tabla, info in metadata.items():

        columnas = info.get("columns", [])

        # =========================
        # CLASIFICACIÓN empresa_id
        # =========================
        clas, tipo, tiene_empresa = clasificar_empresa_id(columnas)

        # =========================
        # DECISIÓN
        # =========================
        decision = decisiones.get(tabla, "EXCLUDE")

        # =========================
        # CLASIFICACIÓN FUNCIONAL (CORE / CATALOGO / TRANSACCIONAL)
        # =========================
        tipo_tabla = clasificacion_tablas.get(tabla, "UNKNOWN")

        row = {
            "tabla": tabla,
            "clasificacion_tabla": tipo_tabla, 
            "clasificacion": clas,
            "tipo_empresa_id": tipo,
            "tiene_empresa_id": tiene_empresa,
            "decision": decision
        }

        # =========================
        # SQL FIX
        # =========================
        row["sql_fix"] = generar_sql(row)

        data.append(row)

    return pd.DataFrame(data)