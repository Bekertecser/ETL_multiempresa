import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# BASE
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# =========================
# DB (IMPORTANTE PARA LOGS)
# =========================
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")

# =========================
# ARCHIVOS
# =========================
EXCEL_PATH = os.getenv(
    "EXCEL_PATH",
    os.path.join(BASE_DIR, "data", "input.xlsx")
)

LOG_FILE = os.getenv(
    "LOG_FILE",
    os.path.join(BASE_DIR, "logs", "etl.log")
)

SQL_FOLDER = os.getenv(
    "SQL_FOLDER",
    os.path.join(BASE_DIR, "sql")
)

# =========================
# ETL CONTROL
# =========================
CHUNKSIZE = int(os.getenv("CHUNKSIZE", 1000))

TRUNCATE_BEFORE_LOAD = (
    os.getenv("TRUNCATE_BEFORE_LOAD", "true").lower() == "true"
)

# =========================
# DEBUG / LOGGING
# =========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# =========================
# VALIDACIONES
# =========================
REQUIRED_ENV_VARS = [
    "DB_SERVER",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_DRIVER"
]

missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

if missing:
    raise Exception(f"❌ Variables faltantes en .env: {missing}")

# =========================
# CREAR CARPETAS SI NO EXISTEN
# =========================
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)
os.makedirs(SQL_FOLDER, exist_ok=True)