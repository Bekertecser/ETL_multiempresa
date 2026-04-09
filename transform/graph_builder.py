from collections import defaultdict


def build_graph(metadata):
    """
    Construye métricas de relaciones:
    - fk_count: cuántas FK tiene la tabla (dependencias)
    - referenced_by: cuántas tablas dependen de ella (centralidad)
    """

    fk_count = defaultdict(int)
    referenced_by = defaultdict(int)

    for tabla, data in metadata.items():
        fks = data.get("foreign_keys", [])

        fk_count[tabla] = len(fks)

        for fk in fks:
            parent = fk.get("referred_table")
            if parent:
                referenced_by[parent] += 1

    return fk_count, referenced_by