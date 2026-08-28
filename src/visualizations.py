import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DB_PATH = "database/retail_dw.db"
OUTPUT_DIR = "docs"

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo",
    4: "Abril", 5: "Mayo", 6: "Junio",
}

sns.set_theme(style="whitegrid", font_scale=1.05)


def plot_monthly_net_sales_trend(conn, output_dir=OUTPUT_DIR):
    """Visualizacion 1 (temporal, R1): tendencia mensual de ventas netas."""
    df = pd.read_sql_query("""
        SELECT d.month AS mes_num, ROUND(SUM(f.net_sales), 0) AS ventas_netas
        FROM fact_sales f
        JOIN dim_dates d ON f.date_id = d.date_id
        GROUP BY d.month
        ORDER BY d.month;
    """, conn)
    df["mes"] = df["mes_num"].map(MESES)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.lineplot(data=df, x="mes", y="ventas_netas", marker="o", linewidth=2.5,
                 color="#2E5EAA", markersize=9, ax=ax)
    ax.fill_between(range(len(df)), df["ventas_netas"], alpha=0.08, color="#2E5EAA")

    ax.set_title("R1 · Tendencia mensual de ventas netas", fontsize=15, weight="bold", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("Ventas netas (COP)")
    ax.yaxis.set_major_formatter(lambda x, _: f"${x/1e6:,.0f}M")
    sns.despine()

    fig.tight_layout()
    path = f"{output_dir}/viz1_tendencia_ventas_mensuales.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[SUCCESS] Visualizacion 1 guardada en {path}")


def plot_sales_by_category_brand(conn, output_dir=OUTPUT_DIR):
    """Visualizacion 2 (comparativa, R3): ventas netas por categoria y marca."""
    df = pd.read_sql_query("""
        SELECT p.category AS categoria, p.brand AS marca,
               ROUND(SUM(f.net_sales), 0) AS ventas_netas
        FROM fact_sales f
        JOIN dim_products p ON f.product_key = p.product_key
        GROUP BY p.category, p.brand
        ORDER BY p.category, ventas_netas DESC;
    """, conn)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, x="categoria", y="ventas_netas", hue="marca",
                palette="viridis", ax=ax)

    ax.set_title("R3 · Ventas netas por categoria y marca", fontsize=15, weight="bold", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("Ventas netas (COP)")
    ax.yaxis.set_major_formatter(lambda x, _: f"${x/1e6:,.0f}M")
    ax.legend(title="Marca", frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    sns.despine()

    fig.tight_layout()
    path = f"{output_dir}/viz2_ventas_categoria_marca.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"[SUCCESS] Visualizacion 2 guardada en {path}")


def generate_visualizations(db_path=DB_PATH, output_dir=OUTPUT_DIR):
    conn = sqlite3.connect(db_path)
    plot_monthly_net_sales_trend(conn, output_dir)
    plot_sales_by_category_brand(conn, output_dir)
    conn.close()


if __name__ == "__main__":
    generate_visualizations()