# schema mejorado :D
import sqlite3
import os

# Este archivo se encarga de crear el esquema en estrella para el Data Mart de Ventas. 

DB_PATH = "database/retail_dw.db" # Ruta de la base de datos


def create_schema(db_path=DB_PATH): # crear esquema en estrella

    # Asegura que la carpeta database exista antes de crear el archivo
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path) # Conexión a la base de datos
    cursor = conn.cursor()

    # Habilitar soporte de claves foráneas en SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Eliminar tablas si existen (para reiniciar el esquema) (discutible pero diria es lo mejor para este caso)
    cursor.executescript("""
        DROP TABLE IF EXISTS fact_sales;
        DROP TABLE IF EXISTS dim_stores;
        DROP TABLE IF EXISTS dim_channels;
        DROP TABLE IF EXISTS dim_products;
        DROP TABLE IF EXISTS dim_promotions;
        DROP TABLE IF EXISTS dim_dates;
    """)

    # DDL: Dimensión Tiempo (dim_dates)
    # PK = date_id (smart key en formato YYYYMMDD), no requiere subrogada adicional
    cursor.execute("""
        CREATE TABLE dim_dates (
            date_id INTEGER PRIMARY KEY,   -- Formato YYYYMMDD
            year    INTEGER NOT NULL,
            month   INTEGER NOT NULL,
            day     INTEGER NOT NULL
        );
    """)

    # DDL: Dimensión Canal (dim_channels)
    cursor.execute("""
        CREATE TABLE dim_channels (
            channel_key  INTEGER PRIMARY KEY AUTOINCREMENT,  -- subrogada
            channel_id   TEXT NOT NULL UNIQUE,               -- natural ("C01")
            channel_name TEXT NOT NULL
        );
    """)

    # DDL: Dimensión Tienda (dim_stores)    
    cursor.execute("""
        CREATE TABLE dim_stores (
            store_key  INTEGER PRIMARY KEY AUTOINCREMENT,  -- subrogada
            store_id   TEXT NOT NULL UNIQUE,               -- natural ("S01")
            store_name TEXT NOT NULL,
            city       TEXT NOT NULL,
            region     TEXT NOT NULL
        );
    """)

    # DDL: Dimensión Producto (dim_products)
    cursor.execute("""
        CREATE TABLE dim_products (
            product_key  INTEGER PRIMARY KEY AUTOINCREMENT,  -- subrogada
            product_id   TEXT NOT NULL UNIQUE,               -- natural ("P001")
            product_name TEXT NOT NULL,
            category     TEXT NOT NULL,
            brand        TEXT NOT NULL,
            list_price   REAL NOT NULL,
            unit_cost    REAL NOT NULL
        );
    """)

    # DDL: Dimensión Promoción (dim_promotions)
    cursor.execute("""
        CREATE TABLE dim_promotions (
            promotion_key  INTEGER PRIMARY KEY AUTOINCREMENT,  -- subrogada
            promotion_id   TEXT NOT NULL UNIQUE,               -- natural ("PR00")
            promotion_name TEXT NOT NULL,
            discount_pct   REAL NOT NULL
        );
    """)

    # DDL: Tabla de Hechos (fact_sales)
    # una fila = una línea de venta (sale_line_id, ya único en origen)
    cursor.execute("""
        CREATE TABLE fact_sales (
            sale_line_id    TEXT PRIMARY KEY,
            date_id         INTEGER NOT NULL,
            store_key       INTEGER NOT NULL,
            channel_key     INTEGER NOT NULL,
            product_key     INTEGER NOT NULL,
            promotion_key   INTEGER NOT NULL,
            quantity        INTEGER NOT NULL,
            gross_sales     REAL NOT NULL,
            net_sales       REAL NOT NULL,
            discount_amount REAL NOT NULL,
            total_cost      REAL NOT NULL,
            gross_profit    REAL NOT NULL,
            FOREIGN KEY (date_id)       REFERENCES dim_dates(date_id),
            FOREIGN KEY (store_key)     REFERENCES dim_stores(store_key),
            FOREIGN KEY (channel_key)   REFERENCES dim_channels(channel_key),
            FOREIGN KEY (product_key)   REFERENCES dim_products(product_key),
            FOREIGN KEY (promotion_key) REFERENCES dim_promotions(promotion_key)
        );
    """)

    conn.commit() 
    conn.close()
    print(f"[SUCCESS] Esquema en estrella creado correctamente en {db_path}")


if __name__ == "__main__":
    create_schema()