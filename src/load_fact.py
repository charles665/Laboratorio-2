
# Tarea: acomodar la carga de las facts con base a nuestros datos de referencia, para que se pueda cargar el datamart sin errores.

import sqlite3
import numpy as np

def load_fact_sales(db_path="sales_datamart.db", num_records=1000):
    """
    Genera y carga las transacciones de ventas a nivel de grano declarado.
    Calcula: Gross Sales, Discount Amount, Net Sales, Total Cost y Gross Profit.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Obtener llaves válidas desde las dimensiones creadas
    dates = [row[0] for row in cursor.execute("SELECT date_id FROM dim_dates").fetchall()]
    stores = [row[0] for row in cursor.execute("SELECT store_id FROM dim_stores").fetchall()]
    channels = [row[0] for row in cursor.execute("SELECT channel_id FROM dim_channels").fetchall()]

    # store_channel_map = {row[0]: row[1] for row in cursor.execute("SELECT store_id, channel_id FROM dim_stores").fetchall()}
    
    products = cursor.execute("SELECT product_id, list_price, unit_cost FROM dim_products").fetchall()
    prod_map = {p[0]: (p[1], p[2]) for p in products}
    
    promotions = cursor.execute("SELECT promotion_id, discount_pct FROM dim_promotions").fetchall()
    promo_map = {pr[0]: pr[1] for pr in promotions}
    
    np.random.seed(42)
    fact_records = []
    
    for _ in range(num_records):
        d_id = int(np.random.choice(dates))
        s_id = int(np.random.choice(stores))
        c_id = int(np.random.choice(channels))
        #Producto Id
        p_id = int(np.random.choice(list(prod_map.keys())))
        #Promoción Id
        pr_id = int(np.random.choice(list(promo_map.keys()), p=[0.5, 0.2, 0.15, 0.15])) # 50% transacciones sin promo
        
        quantity = int(np.random.randint(1, 6))
        
        list_price, unit_cost = prod_map[p_id]
        discount_pct = promo_map[pr_id]
        
        # Cálculos de Métricas
        gross_sales = round(quantity * list_price, 2)
        net_sales = round(quantity * unit_cost, 2)
        discount_amount = round(gross_sales * discount_pct, 2)
        total_cost = round(quantity * unit_cost, 2)
        gross_profit = round(net_sales - total_cost, 2)
        
        fact_records.append((
            d_id, s_id, c_id, p_id, pr_id,
            quantity, gross_sales, net_sales, discount_amount, total_cost, gross_profit
        ))
        
    cursor.executemany("""
        INSERT INTO fact_sales (
            date_id, store_id, channel_id, product_id, promotion_id,
            quantity, gross_sales, net_sales, discount_amount, total_cost, gross_profit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fact_records)
    
    conn.commit()
    conn.close()
    print(f"[SUCCESS] {num_records} registros cargados en fact_sales correctamente.")

if __name__ == "__main__":
    load_fact_sales()