from create_schema import create_schema
from load_dimensions import load_all_dimensions
from load_fact import load_fact_sales
from queries import run_queries
from visualizations import generate_visualizations

DB_PATH = "database/retail_dw.db"
JSON_PATH = "data/reference_data.json"
CSV_PATH = "data/sales_transactions.csv"


def main(): # Ejecuta el pipeline completo del Data Mart de ventas: crea el esquema, carga dimensiones y hechos, ejecuta consultas y genera visualizaciones.
    print("========================================================")
    print("EJECUTANDO PIPELINE COMPLETO DEL DATA MART DE VENTAS")
    print("========================================================")

    print("\nPaso 1: Creando esquema en estrella...")
    create_schema(DB_PATH)

    print("\nPaso 2: Cargando dimensiones desde reference_data.json...")
    load_all_dimensions(DB_PATH, JSON_PATH, CSV_PATH)

    print("\nPaso 3: Cargando fact_sales desde sales_transactions.csv...")
    load_fact_sales(DB_PATH, CSV_PATH)

    print("\nPaso 4: Ejecutando consultas analiticas de negocio (R1-R5)...")
    run_queries(DB_PATH)

    print("\nPaso 5: Generando visualizaciones...")
    generate_visualizations(DB_PATH)

    print("\n========================================================")
    print("[COMPLETADO] El Data Mart ha sido creado, cargado y validado.")
    print("========================================================")


if __name__ == "__main__":
    main()