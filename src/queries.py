import sqlite3
import pandas as pd

DB_PATH = "database/retail_dw.db"

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo",
    4: "Abril", 5: "Mayo", 6: "Junio",
}

def run_queries(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)

    print("\n========================================================")
    print("R1: TENDENCIA MENSUAL DE VENTAS NETAS")
    print("========================================================")
    r1 = pd.read_sql_query("""
        SELECT
            d.year AS Anio,
            d.month AS Mes_Num,
            ROUND(SUM(f.net_sales), 2) AS Ventas_Netas_Totales
        FROM fact_sales f
        JOIN dim_dates d ON f.date_id = d.date_id
        GROUP BY d.year, d.month
        ORDER BY d.year, d.month;
    """, conn)
    r1["Mes"] = r1["Mes_Num"].map(MESES)
    print(r1.to_string(index=False))

    print("\n========================================================")
    print("R2: COMPARACIÓN DE RENDIMIENTO POR TIENDA Y CANAL")
    print("========================================================")
    r2 = pd.read_sql_query("""
        SELECT
            s.store_name AS Tienda,
            c.channel_name AS Canal,
            SUM(f.quantity) AS Unidades_Vendidas,
            ROUND(SUM(f.net_sales), 2) AS Ventas_Netas
        FROM fact_sales f
        JOIN dim_stores s ON f.store_key = s.store_key
        JOIN dim_channels c ON f.channel_key = c.channel_key
        GROUP BY s.store_name, c.channel_name
        ORDER BY Ventas_Netas DESC;
    """, conn)
    print(r2.to_string(index=False))

    print("\n========================================================")
    print("R3: MEJORES CATEGORÍAS Y MARCAS (REVENUE Y UNIDADES)")
    print("========================================================")
    r3 = pd.read_sql_query("""
        SELECT
            p.category AS Categoria,
            p.brand AS Marca,
            SUM(f.quantity) AS Unidades_Vendidas,
            ROUND(SUM(f.net_sales), 2) AS Ingresos_Totales
        FROM fact_sales f
        JOIN dim_products p ON f.product_key = p.product_key
        GROUP BY p.category, p.brand
        ORDER BY Ingresos_Totales DESC;
    """, conn)
    print(r3.to_string(index=False))

    print("\n========================================================")
    print("R4: EVALUACIÓN DE EFECTIVIDAD DE PROMOCIONES")
    print("========================================================")
    r4 = pd.read_sql_query("""
        SELECT
            pr.promotion_name AS Promocion,
            COUNT(f.sale_line_id) AS Num_Lineas_Venta,
            SUM(f.quantity) AS Unidades_Vendidas,
            ROUND(SUM(f.gross_sales), 2) AS Ventas_Brutas,
            ROUND(SUM(f.discount_amount), 2) AS Descuento_Total,
            ROUND(SUM(f.net_sales), 2) AS Ventas_Netas
        FROM fact_sales f
        JOIN dim_promotions pr ON f.promotion_key = pr.promotion_key
        GROUP BY pr.promotion_name
        ORDER BY Ventas_Netas DESC;
    """, conn)
    print(r4.to_string(index=False))

    print("\n========================================================")
    print("R5: MARGEN BRUTO (%) POR CATEGORÍA, TIENDA Y MES (TOP 10)")
    print("========================================================")
    r5 = pd.read_sql_query("""
        SELECT
            d.month AS Mes_Num,
            s.store_name AS Tienda,
            p.category AS Categoria,
            ROUND(SUM(f.gross_sales), 2) AS Ingresos_Brutos,
            ROUND(SUM(f.net_sales), 2) AS Ventas_Netas,
            ROUND(SUM(f.total_cost), 2) AS Costo_Total,
            ROUND(SUM(f.gross_profit), 2) AS Ganancia_Bruta,
            ROUND((SUM(f.gross_profit) / SUM(f.net_sales)) * 100, 2) AS Margen_Bruto_Pct
        FROM fact_sales f
        JOIN dim_dates d ON f.date_id = d.date_id
        JOIN dim_stores s ON f.store_key = s.store_key
        JOIN dim_products p ON f.product_key = p.product_key
        GROUP BY d.month, s.store_name, p.category
        ORDER BY d.month ASC, s.store_name, p.category;
    """, conn)
    r5["Mes"] = r5["Mes_Num"].map(MESES)
    print(r5.head(10).to_string(index=False))

    conn.close()


if __name__ == "__main__":
    run_queries()