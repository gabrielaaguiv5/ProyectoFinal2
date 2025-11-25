# =========================================================
#  SmartChat Insight
#  Análisis, clasificación de clientes y exportación final para Power BI
# =========================================================

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import warnings
import sys
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings("ignore", category=UserWarning)

# =========================================================
# RUTAS RELATIVAS UNIVERSALES
# =========================================================

# /src → sube al proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CLEAN_PATH = DATA_DIR / "cleaned"
OUTPUT_PATH = DATA_DIR / "outputs"
FINAL_PATH = OUTPUT_PATH / "final"

# Crear carpetas si no existen
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
FINAL_PATH.mkdir(parents=True, exist_ok=True)

# Palabras clave
PRODUCTOS_CLAVE = [
    "vidrio", "fachada", "aluminio", "puerta", "ventana",
    "baño", "división", "pasamanos", "pérgola", "instalador"
]

# ---------------------------------------------------------
# Funciones
# ---------------------------------------------------------


def clasificar_cliente(dias: int) -> str:
    if dias <= 15:
        return "Frecuente"
    elif dias <= 45:
        return "Inactivo reciente"
    else:
        return "Perdido"


def generate_plots(activity_df: pd.DataFrame, products_df: pd.DataFrame):
    """Genera gráficos automáticos en la carpeta outputs."""

    # ---- Gráfico 1 ----
    plt.figure(figsize=(8, 5))
    activity_df["estado"].value_counts().plot(kind="bar", color='#3b82f6')
    plt.title("Distribución de Clientes por Estado")
    plt.xlabel("Estado")
    plt.ylabel("Número de clientes")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / "clientes_estado_distribucion.png")
    plt.close()

    # ---- Gráfico 2 ----
    plt.figure(figsize=(10, 6))
    products_df.set_index("producto")["menciones"].sort_values().plot(
        kind="barh", color='#10b981'
    )
    plt.title("Productos más mencionados")
    plt.xlabel("Número de menciones")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(OUTPUT_PATH / "productos_mas_mencionados.png")
    plt.close()


# ---------------------------------------------------------
# Función principal
# ---------------------------------------------------------

def run_analysis_and_export(df: pd.DataFrame):
    print("\n[FASE DE ANALISIS] Iniciando análisis de actividad y productos...")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(subset=['date'], inplace=True)

    if df.empty:
        print("ADVERTENCIA: DataFrame vacío. No se puede realizar el análisis.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    print(f"-> Total de mensajes a analizar: {len(df)}")

    activity = (
        df.groupby("user")
          .agg(
              mensajes=("message", "count"),
              primer_contacto=("date", "min"),
              ultimo_contacto=("date", "max")
        )
        .reset_index()
    )

    max_date = df["date"].max()
    activity["dias_desde_ultimo"] = (
        max_date - activity["ultimo_contacto"]).dt.days
    activity["estado"] = activity["dias_desde_ultimo"].apply(
        clasificar_cliente)

    conteo_productos = {
        p: df["message"].str.contains(p, case=False, na=False).sum()
        for p in PRODUCTOS_CLAVE
    }

    df_productos = pd.DataFrame(
        list(conteo_productos.items()),
        columns=["producto", "menciones"]
    ).sort_values(by="menciones", ascending=False)

    menciones_por_cliente = []
    for user, mensajes in df.groupby("user"):
        registro = {"user": user}
        for p in PRODUCTOS_CLAVE:
            registro[p] = mensajes["message"].str.contains(
                p, case=False, na=False).sum()
        menciones_por_cliente.append(registro)

    df_clientes_productos = pd.DataFrame(menciones_por_cliente)

    # Producto más mencionado por cada cliente
    df_clientes_productos["producto_preferido"] = df_clientes_productos[PRODUCTOS_CLAVE].idxmax(
        axis=1)
    df_clientes_productos["menciones_producto_preferido"] = df_clientes_productos.apply(
        lambda row: row[row["producto_preferido"]], axis=1
    )

    # Unir con tabla de actividad
    clientes_final = activity.merge(
        df_clientes_productos[[
            "user", "producto_preferido", "menciones_producto_preferido"]],
        on="user",
        how="left"
    )

    generate_plots(activity, df_productos)

    print("\n[FASE DE EXPORTACION] Exportando archivos finales...")

    clientes_final.columns = clientes_final.columns.str.lower().str.replace(" ", "_")
    df_productos.columns = df_productos.columns.str.lower().str.replace(" ", "_")

    resumen_clientes = (
        clientes_final.groupby("estado")
        .agg(
            total_clientes=("user", "count"),
            promedio_mensajes=("mensajes", "mean"),
            dias_promedio_inactividad=("dias_desde_ultimo", "mean")
        )
        .reset_index()
    )

    resumen_clientes["promedio_mensajes"] = resumen_clientes["promedio_mensajes"].round(
        1)
    resumen_clientes["dias_promedio_inactividad"] = resumen_clientes["dias_promedio_inactividad"].round(
        1)
    resumen_clientes["fecha_reporte"] = datetime.now().strftime("%Y-%m-%d")

    # Guardado final en rutas RELATIVAS
    clientes_final.to_csv(FINAL_PATH / "clientes_final_powerbi.csv",
                          index=False, encoding="utf-8-sig", sep=";")
    df_productos.to_csv(FINAL_PATH / "productos_powerbi.csv",
                        index=False, encoding="utf-8-sig", sep=";")
    resumen_clientes.to_csv(FINAL_PATH / "resumen_clientes.csv",
                            index=False, encoding="utf-8-sig", sep=";")

    print("✅ Exportación final completada.")
    print(f"Archivos guardados en: {FINAL_PATH}")

    return clientes_final, df_productos, resumen_clientes

# ---------------------------------------------------------
# Entrada de prueba
# ---------------------------------------------------------


if __name__ == "__main__":
    print("Ejecutando prueba del módulo de análisis...")

    clean_data_path = CLEAN_PATH / "whatsapp_clean.csv"

    try:
        if not clean_data_path.exists():
            print(f"❌ ERROR: Archivo no encontrado: {clean_data_path}")
        else:
            df_clean = pd.read_csv(clean_data_path, encoding="utf-8")
            run_analysis_and_export(df_clean)

    except Exception as e:
        print(f"❌ Error fatal: {e}")
