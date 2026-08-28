#Tarea: acomodar la carga de las dimensiones con base a nueestros datos de referencia, para que se pueda cargar el datamart sin errores.

import sqlite3
from datetime import datetime, timedelta

def load_channels(conn):
    channels = [
        (1, 'Tienda Física'),
        (2, 'Tienda Online')
    ]
    conn.executemany("INSERT INTO dim_channels VALUES (?, ?)", channels)

def load_stores(conn):
    stores = [
        (101, 'Tienda Alpha - Centro', 'Bogotá', 'Andina', 1),
        (102, 'Tienda Beta - Norte', 'Medellín', 'Antioquia', 1),
        (103, 'Tienda Nacional Online', 'E-Commerce', 'Nacional', 2)
    ]
    conn.executemany("INSERT INTO dim_stores VALUES (?, ?, ?, ?, ?)", stores)

def load_dates(conn, start_date_str="2026-01-01", end_date_str="2026-06-30"):
    """Genera la dimensión de tiempo contigua para 6 meses."""
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    curr = start_date
    dates_data = []
    
    # Nombres de meses y días en español
    months_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio'}
    days_es = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 
               'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
    
    while curr <= end_date:
        date_id = int(curr.strftime("%Y%m%d"))
        day_name = days_es.get(curr.strftime("%A"), curr.strftime("%A"))
        month_name = months_es.get(curr.month, curr.strftime("%B"))
        quarter = (curr.month - 1) // 3 + 1
        
        dates_data.append((
            date_id,
            curr.strftime("%Y-%m-%d"),
            curr.year,
            curr.month,
            month_name,
            curr.day,
            day_name,
            quarter
        ))
        curr += timedelta(days=1)
        
    conn.executemany("INSERT INTO dim_dates VALUES (?, ?, ?, ?, ?, ?, ?, ?)", dates_data)

def load_products(conn):
    products = [
        (1, 'Laptop Pro 15', 'Electrónica', 'TechBrand', 1200.00, 800.00),
        (2, 'Smartphone X', 'Electrónica', 'MobileCorp', 800.00, 500.00),
        (3, 'Audífonos Inalámbricos', 'Audio', 'SoundMaster', 150.00, 70.00),
        (4, 'Monitor Inteligente 27"', 'Electrónica', 'VisionTech', 350.00, 220.00),
        (5, 'Teclado Ergonómico', 'Accesorios', 'KeyPro', 80.00, 40.00)
    ]
    conn.executemany("INSERT INTO dim_products VALUES (?, ?, ?, ?, ?, ?)", products)

def load_promotions(conn):
    promotions = [
        (0, 'Sin Promoción', 0.00),
        (1, 'Descuento Año Nuevo', 0.15),
        (2, 'Liquidación Primavera', 0.20),
        (3, 'Cyber Flash Discount', 0.25)
    ]
    conn.executemany("INSERT INTO dim_promotions VALUES (?, ?, ?)", promotions)

def load_all_dimensions(db_path="sales_datamart.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    load_channels(conn)
    load_stores(conn)
    load_dates(conn)
    load_products(conn)
    load_promotions(conn)
    
    conn.commit()
    conn.close()
    print("[SUCCESS] Todas las tablas de dimensión han sido cargadas exitosamente.")

if __name__ == "__main__":
    load_all_dimensions()