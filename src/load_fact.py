import sqlite3
import numpy as np
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent))
from etl.extract import extract_from_csv

DB_PATH = "database/retail_dw.db"
CSV_PATH = "data/sales_transactions.csv"


def load_dimension_tables(conn): # Carga todas las dimensiones desde el CSV de transacciones de ventas y devuelve un diccionario con DataFrames de cada dimensión, incluyendo las llaves subrogadas necesarias para construir la tabla de hechos.
    
    return { 
        "stores": pd.read_sql("SELECT store_key, store_id FROM dim_stores", conn),
        "channels": pd.read_sql("SELECT channel_key, channel_id FROM dim_channels", conn),
        "products": pd.read_sql(
            "SELECT product_key, product_id, list_price, unit_cost FROM dim_products", conn
        ),
        "promotions": pd.read_sql(
            "SELECT promotion_key, promotion_id FROM dim_promotions", conn
        ),
    }


def build_fact_dataframe(sales_df, dims): # Calcula las llaves subrogadas y medidas necesarias para construir la tabla de hechos fact_sales a partir del DataFrame de transacciones de ventas y los DataFrames de dimensiones.
  
    df = sales_df.copy() # Copia del DataFrame de ventas para no modificar el original

    # date_id como YYYYMMDD, igual formato que dim_dates
    df["date_id"] = (
        pd.to_datetime(df["sale_date"]).dt.strftime("%Y%m%d").astype(int)
    )

    # Mapeo de IDs naturales a llaves subrogadas via merge
    df = df.merge(dims["stores"], on="store_id", how="left")
    df = df.merge(dims["channels"], on="channel_id", how="left")
    df = df.merge(dims["products"], on="product_id", how="left")
    df = df.merge(dims["promotions"], on="promotion_id", how="left")

    # Validacion: si algun merge no encontro coincidencia, la llave queda NaN
    llaves = ["store_key", "channel_key", "product_key", "promotion_key"]
    huerfanos = df[df[llaves].isna().any(axis=1)]
    if not huerfanos.empty:
        raise ValueError(
            f"Se encontraron {len(huerfanos)} filas sin coincidencia en las dimensiones:\n"
            f"{huerfanos[['sale_line_id'] + llaves]}"
        )

    # Calculo de medidas
    df["gross_sales"] = df["quantity"] * df["list_price"]
    df["net_sales"] = df["quantity"] * df["unit_price_sale"]
    df["discount_amount"] = df["gross_sales"] - df["net_sales"]
    df["total_cost"] = df["quantity"] * df["unit_cost"]
    df["gross_profit"] = df["net_sales"] - df["total_cost"]

    columnas_finales = [ # Seleccion de columnas finales para la tabla de hechos
        "sale_line_id", "date_id", "store_key", "channel_key",
        "product_key", "promotion_key", "quantity",
        "gross_sales", "net_sales", "discount_amount",
        "total_cost", "gross_profit",
    ]
    return df[columnas_finales] 


def load_fact_sales(db_path=DB_PATH, csv_path=CSV_PATH): # Carga la tabla de hechos fact_sales desde el CSV de transacciones de ventas, calculando las llaves subrogadas y medidas necesarias a partir de las dimensiones ya cargadas.
 
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")  # valida integridad referencial

    # Extrae las ventas crudas del CSV
    sales_files = extract_from_csv(csv_path)
    sales_df = next(iter(sales_files.values()))

    # Mapea IDs naturales, llaves subrogadas y calcula las medidas
    dims = load_dimension_tables(conn)
    fact_df = build_fact_dataframe(sales_df, dims)

    # Inserta todas las filas en una sola operacion batch
    records = list(fact_df.itertuples(index=False, name=None))
    conn.executemany(
        """INSERT INTO fact_sales
           (sale_line_id, date_id, store_key, channel_key, product_key,
            promotion_key, quantity, gross_sales, net_sales,
            discount_amount, total_cost, gross_profit)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        records,
    )

    conn.commit()
    filas_cargadas = conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0]
    conn.close()
    print(f"[SUCCESS] fact_sales cargada con {filas_cargadas} filas.")


if __name__ == "__main__":
    load_fact_sales()