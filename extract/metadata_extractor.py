from sqlalchemy import inspect
from config.db import get_engine


def get_metadata(engine):
    """
    Extrae metadata completa de la base de datos:
    - Tablas
    - Columnas (nombre, tipo, nullability)
    - Llaves foráneas
    - Índices

    Returns:
        dict: estructura completa de metadata
    """
    inspector = inspect(engine)

    tablas = inspector.get_table_names()

    metadata = {}

    for tabla in tablas:
        metadata[tabla] = {
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": col.get("default")
                }
                for col in inspector.get_columns(tabla)
            ],
            "primary_key": inspector.get_pk_constraint(tabla),
            "foreign_keys": inspector.get_foreign_keys(tabla),
            "indexes": inspector.get_indexes(tabla)
        }

    return metadata


if __name__ == "__main__":
    # 🔍 Debug / ejecución directa
    import json

    metadata = get_metadata()

    print(json.dumps(metadata, indent=4, ensure_ascii=False))