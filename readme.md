# ETL Multiempresa - Análisis de Arquitectura de Base de Datos

## 📋 Descripción General

Este proyecto es un **ETL (Extract, Transform, Load)** diseñado para analizar la arquitectura y estructura de una base de datos SQL Server, con enfoque en identificar patrones de relacionamiento y clasificar tablas para un modelo multiempresa.

### Objetivo Principal
Extraer metadata de una base de datos, construir un grafo de relaciones, clasificar las tablas según su rol arquitectónico y generar recomendaciones para implementar un modelo multiempresa escalable.

---

## 🏗️ Arquitectura del Proyecto

```
ETL_multiempresa/
├── main.py                 # Orquestador principal del ETL
├── requirements.txt        # Dependencias del proyecto
├── readme.md              # Este archivo
│
├── config/
│   ├── db.py              # Configuración de conexión a BD
│   └── settings.py        # Configuración general de la aplicación
│
├── extract/
│   └── metadata_extractor.py    # Extracción de metadata de la BD
│
├── transform/
│   ├── graph_builder.py         # Construcción del grafo de relaciones
│   ├── classifier.py            # Clasificación de tablas
│   └── rules_engine.py          # Motor de decisiones
│
├── load/
│   └── exporter.py              # Exportación a Excel
│
├── utils/
│   └── logger.py                # Sistema de logging
│
├── data/                   # Datos de entrada
├── logs/                   # Archivos de log
├── output/                 # Archivos de salida
├── sql/                    # Scripts SQL generados
└── notebooks/
    └── exploracion.ipynb   # Análisis exploratorio
```

---

## 🔄 Flujo del ETL

```
1. SETUP LOGGER
   ↓
2. CONEXIÓN BD
   ↓
3. EXTRACIÓN DE METADATA
   ├── Tablas
   ├── Columnas y tipos
   ├── Llaves primarias
   ├── Llaves foráneas
   └── Índices
   ↓
4. CONSTRUCCIÓN DE GRAFO
   ├── Conteo de relaciones FK
   └── Análisis de centralidad (referenced_by)
   ↓
5. CLASIFICACIÓN DE TABLAS
   ├── CORE (tablas centrales)
   ├── TRANSACCIONAL (tablas de operaciones)
   └── CATALOGO (tablas de referencia)
   ↓
6. APLICACIÓN DE REGLAS
   ├── Decisión INCLUDE/EXCLUDE
   └── Análisis de empresa_id
   ↓
7. EXPORTACIÓN
   └── DataFrame a Excel
```

---

## 📦 Módulos Principales

### 1. **config/db.py** - Conexión a Base de Datos
Maneja la conexión con SQL Server usando SQLAlchemy.

**Funciones:**
- `get_connection_string()` - Construye la cadena de conexión desde variables de entorno
- `get_engine()` - Retorna un engine de SQLAlchemy configurado

**Características:**
- Soporte para MSSQL con pyodbc
- Cifrado de credenciales vía variables de entorno
- Optimización `fast_executemany` para inserciones masivas

---

### 2. **extract/metadata_extractor.py** - Extracción de Metadata
Utiliza SQLAlchemy Inspector para extraer la estructura completa de la BD.

**Función principal:**
```python
get_metadata(engine) -> dict
```

**Retorna estructura:**
```python
{
    "tabla1": {
        "columns": [
            {"name": "id", "type": "BIGINT", "nullable": False, "default": None},
            {"name": "empresa_id", "type": "UNIQUEIDENTIFIER", "nullable": True, ...}
        ],
        "primary_key": {"constrained_columns": ["id"]},
        "foreign_keys": [
            {"name": "FK_tabla1_tabla2", "referred_table": "tabla2", ...}
        ],
        "indexes": [...]
    },
    ...
}
```

---

### 3. **transform/graph_builder.py** - Construcción del Grafo
Analiza las relaciones de llaves foráneas para construir el grafo de dependencias.

**Función principal:**
```python
build_graph(metadata) -> tuple(dict, dict)
```

**Retorna:**
- `fk_count`: Número de relaciones que cada tabla tiene (dependencias directas)
- `referenced_by`: Número de tablas que referencian a cada tabla (centralidad)

**Ejemplo:**
```python
# Si tabla_pedidos tiene FK a tabla_clientes y tabla_productos
fk_count["tabla_pedidos"] = 2

# Si tabla_clientes es referenciada por 8 tablas
referenced_by["tabla_clientes"] = 8
```

**Por qué grafos:**
- Identifica tablas core que son críticas para la arquitectura
- Detecta dependencias y jerarquías
- Ayuda a planificar la implementación multiempresa

---

### 4. **transform/classifier.py** - Clasificación de Tablas
Clasifica cada tabla en categorías según patrones y características.

**Categorías:**

| Tipo | Criterios | Ejemplos |
|------|-----------|----------|
| **CATALOGO** | Nombres con patrones (tipo_, estado_, etc.), pocas columnas (≤6), poca referencia (<5 tablas) | Estados, Tipos, Parámetros |
| **CORE** | Muy referenciadas (≥5 tablas), múltiples FK | Clientes, Productos, Empleados |
| **TRANSACCIONAL** | Contienen claves temporales (fecha, valor, cantidad) | Pedidos, Facturas, Movimientos |

**Función principal:**
```python
clasificar(metadata, fk_count, referenced_by) -> dict
```

---

### 5. **transform/rules_engine.py** - Motor de Decisiones
Aplica reglas de negocio para decidir qué tablas incluir en el modelo multiempresa.

**Reglas:**
```python
TYPE_RULES = {
    "CORE":           "INCLUDE",      # Incluir en modelo
    "TRANSACCIONAL":  "INCLUDE",      # Incluir en modelo
    "CATALOGO":       "EXCLUDE",      # Excluir
    "SOPORTE":        "EXCLUDE"       # Excluir
}
```

**Función principal:**
```python
decidir(tabla, tipo) -> str  # "INCLUDE" o "EXCLUDE"
```

**Análisis de empresa_id:**
```python
clasificar_empresa_id(columnas) -> tuple
# Retorna: (estado, tipo_dato, existe)
```

---

### 6. **load/exporter.py** - Exportación
Genera un DataFrame con todo el análisis y lo exporta a Excel.

**Contenido del Excel:**
- Tabla
- Clasificación (CORE, TRANSACCIONAL, CATALOGO)
- Decisión (INCLUDE, EXCLUDE)
- Estado empresa_id
- Tipo de datos empresa_id
- SQL recomendado

---

### 7. **utils/logger.py** - Sistema de Logging
Registro centralizado de eventos del ETL.

**Función principal:**
```python
log_event(logger, server, db, action, status, message, rows=None)
```

**Acciones registradas:**
- CONNECT_DB
- EXTRACT_METADATA
- BUILD_GRAPH
- CLASSIFY
- RULES_ENGINE
- EXPORT_DATAFRAME
- EXPORT_EXCEL

---

## ⚙️ Parametrización de la Aplicación

### Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto:

```env
# ================================
# CONEXIÓN A BASE DE DATOS
# ================================
DB_SERVER=tu_servidor_sql.com
DB_NAME=tu_base_de_datos
DB_USER=usuario_sql
DB_PASSWORD=contraseña_segura
DB_DRIVER=ODBC Driver 17 for SQL Server

# ================================
# ARCHIVOS
# ================================
EXCEL_PATH=data/input.xlsx
LOG_FILE=logs/etl.log
SQL_FOLDER=sql

# ================================
# CONFIGURACIÓN ETL
# ================================
CHUNKSIZE=1000
TRUNCATE_BEFORE_LOAD=true
LOG_LEVEL=INFO
```

### Configuración en settings.py

Todos los parámetros se cargan desde `.env` en [config/settings.py](config/settings.py):

```python
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
CHUNKSIZE = int(os.getenv("CHUNKSIZE", 1000))
```

### Reglas Personalizadas

Modifica [transform/rules_engine.py](transform/rules_engine.py) para ajustar el comportamiento:

```python
# Excluir tablas específicas
FORCE_EXCLUDE = {"tabla_temporal", "tabla_debug"}

# Incluir tablas específicas (override)
FORCE_INCLUDE = {"tabla_especial"}

# Modificar reglas por tipo
TYPE_RULES = {
    "CORE": "INCLUDE",
    "TRANSACCIONAL": "INCLUDE",
    "CATALOGO": "EXCLUDE",
}
```

---

## 📚 Conceptos: Grafos y SQLAlchemy

### Grafos en el Análisis

Un **grafo** es una estructura de datos que conecta nodos (tablas) mediante aristas (relaciones).

**En este proyecto:**
```
         ┌─────────────┐
         │  Clientes   │ (CORE)
         └──────┬──────┘
            ┌──┐│└──┐
            │  │    │
    ┌───────┘  │    └────────┐
    │          │             │
┌───▼───┐  ┌───▼───┐  ┌──────▼────┐
│Pedidos│  │Facturas│ │Direcciones│
│(TRANS)│  │(TRANS) │ │(SOPORTE)  │
└───────┘  └───────┘ └───────────┘
    │
    └──► Estado (CATALOGO)
```

**Métricas calculadas:**
- **fk_count**: Cuántas relaciones tiene cada tabla
- **referenced_by**: Cuántas tablas dependen de ella (centralidad)

```python
# Ejemplo
fk_count = {
    "pedidos": 2,        # Tiene FK a clientes y estado
    "clientes": 0,       # No tiene FK
}

referenced_by = {
    "clientes": 5,       # Es referenciada por 5 tablas
    "estado": 12,        # Es referenciada por 12 tablas (muy central)
}
```

**Beneficios:**
- Identifica tablas críticas (high centrality)
- Detecta tablas huérfanas o aisladas
- Ayuda a planificar el orden de carga (jerarquía)
- Visualiza la arquitectura de datos

---

### SQLAlchemy en el Proyecto

**SQLAlchemy** es un ORM (Object-Relational Mapping) que nos permite:

#### 1. **Abstracción de Base de Datos**
```python
from sqlalchemy import create_engine
engine = create_engine("mssql+pyodbc:///?odbc_connect=...")
```
Funciona con SQL Server, PostgreSQL, MySQL, SQLite, etc.

#### 2. **Introspección (Inspection)**
```python
from sqlalchemy import inspect
inspector = inspect(engine)

# Obtener todas las tablas
tablas = inspector.get_table_names()

# Obtener columnas de una tabla
columnas = inspector.get_columns("pedidos")

# Obtener relaciones
fks = inspector.get_foreign_keys("pedidos")
```

**Ventajas:**
- No necesita escribir SQL manualmente
- Uniforme para cualquier BD
- Acceso programático a la metadata

#### 3. **Construcción de Conexiones Seguras**
```python
from urllib.parse import quote_plus
password_safe = quote_plus(password)  # Escapa caracteres especiales
```

#### 4. **Optimización**
```python
create_engine(..., fast_executemany=True)
# Acelera inserciones masivas en MSSQL
```

---

## 🚀 Instalación y Uso

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
# Crear archivo .env con las credenciales de la BD
cp .env.example .env
# Editar .env con los valores reales
```

### 3. Ejecutar el ETL
```bash
python main.py
```

**Salida esperada:**
```
✅ Análisis completado
📁 Archivo generado: output/analisis_empresa_CONTRATOS.xlsx
```

### 4. Revisar Resultados
- **Excel**: `output/analisis_empresa_CONTRATOS.xlsx`
- **Logs**: `logs/etl.log`
- **SQL Scripts**: `sql/` (si se genera)

---

## 📊 Salida del Análisis

El archivo Excel generado contiene:

| Columna | Descripción |
|---------|-------------|
| tabla | Nombre de la tabla |
| clasificacion | CORE / TRANSACCIONAL / CATALOGO |
| decision | INCLUDE / EXCLUDE |
| estado_empresa_id | OK / SIN_EMPRESA_ID / ERROR_TIPO_EMPRESA_ID |
| tipo_empresa_id | Tipo de dato (UNIQUEIDENTIFIER, BIGINT) |
| sql_recomendado | Script SQL para corregir |

---

## 🔍 Ejemplo de Ejecución

```python
# 1. EXTRACCIÓN
metadata = {
    "clientes": {
        "columns": [...],
        "foreign_keys": [],
        "referenced_by_count": 12
    },
    "pedidos": {
        "columns": [...],
        "foreign_keys": ["clientes"],
        "referenced_by_count": 0
    }
}

# 2. GRAFO
fk_count = {"clientes": 0, "pedidos": 1}
referenced_by = {"clientes": 12, "pedidos": 0}

# 3. CLASIFICACIÓN
clasificacion = {
    "clientes": "CORE",
    "pedidos": "TRANSACCIONAL"
}

# 4. DECISIONES
decisiones = {
    "clientes": "INCLUDE",
    "pedidos": "INCLUDE"
}

# 5. EXPORTACIÓN
df.to_excel("output/analisis_empresa_CONTRATOS.xlsx")
```

---

## 🛠️ Troubleshooting

### Error: "No se pudo conectar con la BD"
```bash
# Verificar credenciales en .env
# Verificar que el driver ODBC está instalado
odbc_admin
```

### Error: "No se pudo obtener metadata"
```bash
# Verificar que el usuario tiene permisos SELECT en sys.tables
# Ejecutar como administrador de la BD
```

### El Excel no tiene datos
```bash
# Revisar logs en logs/etl.log
# Verificar que hay tablas en la BD consultada
```

---

## 📝 Licencia y Autor

Proyecto ETL Multiempresa - Beker Martinez Tecser
Diseñado para análisis y arquitectura de bases de datos multiempresa.


