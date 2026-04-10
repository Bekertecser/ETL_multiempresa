from config.db import get_engine
from extract.metadata_extractor import get_metadata
from transform.graph_builder import build_graph
from transform.classifier import clasificar
from transform.rules_engine import decidir
from load.exporter import exportar
from config.settings import LOG_FILE
from utils.logger import setup_logger, log_event

import os


def run():

    # =========================
    # LOGGER
    # =========================
    logger = setup_logger(LOG_FILE)

    server = os.getenv("DB_SERVER")
    db = os.getenv("DB_NAME")

    try:
        # =========================
        # ENGINE
        # =========================
        engine = get_engine()
        log_event(logger, server, db, "CONNECT_DB", "OK", "Conexión creada")

        # =========================
        # METADATA
        # =========================
        metadata = get_metadata(engine)

        if not metadata:
            raise Exception("No se pudo obtener metadata")

        log_event(
            logger,
            server,
            db,
            "EXTRACT_METADATA",
            "OK",
            f"Tablas encontradas: {len(metadata)}",
            rows=len(metadata)
        )

        # =========================
        # GRAFO
        # =========================
        fk_count, referenced_by = build_graph(metadata)

        log_event(
            logger,
            server,
            db,
            "BUILD_GRAPH",
            "OK",
            "Relaciones FK procesadas"
        )

        # =========================
        # CLASIFICACIÓN
        # =========================
        clasificacion = clasificar(metadata, fk_count, referenced_by)

        log_event(
            logger,
            server,
            db,
            "CLASSIFY",
            "OK",
            "Clasificación completada"
        )

        # =========================
        # DECISIONES
        # =========================
        decisiones = {
            tabla: decidir(tabla, clasificacion.get(tabla))
            for tabla in metadata.keys()
        }

        log_event(
            logger,
            server,
            db,
            "RULES_ENGINE",
            "OK",
            "Decisiones aplicadas"
        )
        # =========================
        # EXPORT
        # =========================
        df = exportar(metadata, decisiones, clasificacion)

        log_event(
            logger,
            server,
            db,
            "EXPORT_DATAFRAME",
            "OK",
            "DataFrame generado",
            rows=len(df)
        )

        # =========================
        # OUTPUT
        # =========================
        os.makedirs("output", exist_ok=True)

        output_path = "output/analisis_empresa_CONTRATOS.xlsx"
        df.to_excel(output_path, index=False)

        log_event(
            logger,
            server,
            db,
            "EXPORT_EXCEL",
            "OK",
            f"Archivo generado en {output_path}"
        )

        print("✅ Análisis completado")
        print(f"📁 Archivo generado: {output_path}")

    except Exception as e:
        log_event(
            logger,
            server,
            db,
            "PROCESS",
            "ERROR",
            str(e)
        )
        print("❌ Error en ejecución:", e)


if __name__ == "__main__":
    run()