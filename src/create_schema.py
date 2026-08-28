#Mejor el scheman
import sqlite3

def create_schema(db_path="sales_datamart.db"):
    """
    Crea el esquema en estrella para el Data Mart de Ventas.
    Define dimensiones, tabla de hechos y restricciones de integridad.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Habilitar soporte de claves foráneas en SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Eliminación limpia para re-ejecución del pipeline
    cursor.executescript("""
        DROP TABLE IF EXISTS fact_sales;
        DROP TABLE IF EXISTS dim_stores;
        DROP TABLE IF EXISTS dim_channels;
        DROP TABLE IF EXISTS dim_products;
        DROP TABLE IF EXISTS dim_promotions;
        DROP TABLE IF EXISTS dim_dates;
    """)
    
    # DDL: Tabla Dimensión Canal
    cursor.execute("""
        CREATE TABLE dim_channels (
            channel_id INTEGER PRIMARY KEY,
            channel_name TEXT NOT NULL UNIQUE
        );
    """)
    
    # DDL: Tabla Dimensión Tienda
    cursor.execute("""
        CREATE TABLE dim_stores (
            store_id INTEGER PRIMARY KEY,
            store_name TEXT NOT NULL,
            city TEXT NOT NULL,
            region TEXT NOT NULL,
    """)
    
    # DDL: Tabla Dimensión Tiempo
    cursor.execute("""
        CREATE TABLE dim_dates (
            date_id INTEGER PRIMARY KEY, -- Formato YYYYMMDD
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            day INTEGER NOT NULL,          
        );
    """)
    
    # DDL: Tabla Dimensión Producto
    cursor.execute("""
        CREATE TABLE dim_products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            list_price REAL NOT NULL,
            unit_cost REAL NOT NULL
        );
    """)
    
    # DDL: Tabla Dimensión Promoción
    cursor.execute("""
        CREATE TABLE dim_promotions (
            promotion_id INTEGER PRIMARY KEY,
            promotion_name TEXT NOT NULL,
            discount_pct REAL NOT NULL
        );
    """)
    
    # DDL: Tabla de Hechos Ventas (fact_sales)
    cursor.execute("""
        CREATE TABLE fact_sales (
            sales_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_id INTEGER NOT NULL,
            store_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            promotion_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            gross_sales REAL NOT NULL,
            net_sales REAL NOT NULL,
            discount_amount REAL NOT NULL,
            total_cost REAL NOT NULL,
            gross_profit REAL NOT NULL,
            FOREIGN KEY (date_id) REFERENCES dim_dates(date_id),
            FOREIGN KEY (store_id) REFERENCES dim_stores(store_id),
            FOREIGN KEY (channel_id) REFERENCES dim_channels(channel_id),
            FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
            FOREIGN KEY (promotion_id) REFERENCES dim_promotions(promotion_id)
        );
    """)
    
    conn.commit()
    conn.close()
    print("[SUCCESS] Esquema en estrella creado correctamente.")

if __name__ == "__main__":
    create_schema()