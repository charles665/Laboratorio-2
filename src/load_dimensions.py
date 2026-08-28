import sqlite3
import sys
from pathlib import Path
import pandas as pd


sys.path.append(str(Path(__file__).parent))
from etl.extract import extract_from_csv, extract_from_json # Reutilizar funciones de extract.py

DB_PATH = "database/retail_dw.db" # Ruta de la base de datos
JSON_PATH = "data/reference_data.json" # Ruta del archivo JSON de referencia
CSV_PATH = "data/sales_transactions.csv" # Ruta del archivo CSV de transacciones de ventas


def load_channels(conn, channels_df): # Carga dim_channels
    
    records = list(channels_df[["channel_id", "channel_name"]].itertuples(index=False, name=None)) 
    conn.executemany(
        "INSERT INTO dim_channels (channel_id, channel_name) VALUES (?, ?)", 
        records, 
    )


def load_stores(conn, stores_df): # Carga dim_stores
    
    records = list(
        stores_df[["store_id", "store_name", "city", "region"]].itertuples(index=False, name=None)
    )
    conn.executemany(
        "INSERT INTO dim_stores (store_id, store_name, city, region) VALUES (?, ?, ?, ?)",
        records,
    )


def load_products(conn, products_df): # Carga dim_products con precios de lista y costo, necesarios para las medidas del fact.
    
    records = list( 
        products_df[ 
            ["product_id", "product_name", "category", "brand", "list_price", "unit_cost"]
        ].itertuples(index=False, name=None)
    )
    conn.executemany( 
        """INSERT INTO dim_products
           (product_id, product_name, category, brand, list_price, unit_cost)
           VALUES (?, ?, ?, ?, ?, ?)""",
        records,
    )


def load_promotions(conn, promotions_df): # Carga dim_promotions con porcentaje de descuento, necesario para las medidas del fact.
    
    records = list(
        promotions_df[["promotion_id", "promotion_name", "discount_pct"]].itertuples(
            index=False, name=None
        )
    )
    conn.executemany(
        "INSERT INTO dim_promotions (promotion_id, promotion_name, discount_pct) VALUES (?, ?, ?)",
        records,
    )


def load_dates(conn, sales_df): # Carga dim_dates a partir de las fechas reales que aparecen en sale_date, en vez de un rango fijo.

    unique_dates = pd.to_datetime(sales_df["sale_date"]).dt.normalize().unique() # Obtiene las fechas únicas y normalizadas
    unique_dates = sorted(unique_dates) # Ordena las fechas para consistencia en la carga

    records = []
    for date in unique_dates: # Convierte cada fecha a un formato YYYYMMDD y extrae año, mes y día para la tabla dim_dates
        ts = pd.Timestamp(date)
        date_id = int(ts.strftime("%Y%m%d"))
        records.append((date_id, ts.year, ts.month, ts.day))

    conn.executemany( # Inserta los registros en dim_dates
        "INSERT INTO dim_dates (date_id, year, month, day) VALUES (?, ?, ?, ?)",
        records,
    )


def load_all_dimensions(db_path=DB_PATH, json_path=JSON_PATH, csv_path=CSV_PATH): # Carga todas las dimensiones desde el JSON de referencia y el CSV de transacciones de ventas.
    references = extract_from_json(json_path)
    sales_files = extract_from_csv(csv_path)
    sales_df = next(iter(sales_files.values()))

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")

    load_channels(conn, references["channels"])
    load_stores(conn, references["stores"])
    load_products(conn, references["products"])
    load_promotions(conn, references["promotions"])
    load_dates(conn, sales_df)

    conn.commit()
    conn.close()
    print("[SUCCESS] Todas las tablas de dimension han sido cargadas exitosamente.")


if __name__ == "__main__":
    load_all_dimensions()