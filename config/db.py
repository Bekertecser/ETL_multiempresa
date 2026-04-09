import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def get_connection_string():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER")

    connection_string = f"""
        DRIVER={{{driver}}};
        SERVER={server};
        DATABASE={database};
        UID={username};
        PWD={password};
        TrustServerCertificate=yes;
    """

    return f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"


def get_engine():
    return create_engine(get_connection_string(), fast_executemany=True)