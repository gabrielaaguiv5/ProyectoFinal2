# =========================================================
#  SmartChat Insight
#  Módulo de Predicción y Recomendación (Churn y Similitud)
# =========================================================

import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from pathlib import Path
import numpy as np

# Forzar UTF-8 en Windows para evitar errores con emojis
sys.stdout.reconfigure(encoding="utf-8")

# ===========================
# Rutas relativas universales
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent
FINAL_PATH = BASE_DIR / "data" / "outputs" / "final"


# ---------------------------------------------------------
# Clasificación de riesgo corregida (basada en abandono)
# ---------------------------------------------------------
def clasificar_riesgo(prob_abandono: float) -> str:
    if prob_abandono >= 0.70:
        return "Alto riesgo"
    elif prob_abandono >= 0.40:
        return "Riesgo medio"
    else:
        return "Bajo riesgo"


# ---------------------------------------------------------
# Función principal
# ---------------------------------------------------------
def run_prediction_model():

    print("\n[FASE DE PREDICCIÓN] Iniciando módulo de Machine Learning...\n")

    # -----------------------------------------------------
    # 1. Cargar datos (CORREGIDO)
    # -----------------------------------------------------
    try:
        # --- CORREGIDO: SIN parse_dates ---
        clientes = pd.read_csv(
            FINAL_PATH / "clientes_powerbi.csv",
            sep=";",
            encoding="utf-8",
            engine="python"
        )

        # Manejo opcional de fecha si llega a existir
        if "date" in clientes.columns:
            clientes["date"] = pd.to_datetime(clientes["date"], errors="coerce")

        productos = pd.read_csv(
            FINAL_PATH / "productos_powerbi.csv",
            sep=";",
            encoding="utf-8",
            engine="python"
        )

    except FileNotFoundError as e:
        print("❌ ERROR: No se encuentran los archivos requeridos. Ejecute el módulo de análisis primero.")
        print(f"Detalle: {e}")
        return pd.DataFrame(), None

    except Exception as e:
        print(f"❌ Error al cargar datos: {e}")
        return pd.DataFrame(), None

    # -----------------------------------------------------
    # 2. Limpieza y preparación
    # -----------------------------------------------------
    print("-> Preparando datos para el modelo...")

    clientes["mensajes"] = clientes["mensajes"].fillna(0)
    clientes["dias_desde_ultimo"] = clientes["dias_desde_ultimo"].fillna(0)

    clientes["activo"] = clientes["estado"].apply(
        lambda x: 1 if str(x).lower() in ["frecuente", "inactivo reciente"] else 0
    )

    X = clientes[["mensajes", "dias_desde_ultimo"]]
    y = clientes["activo"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    # -----------------------------------------------------
    # 3. Entrenamiento
    # -----------------------------------------------------
    print("-> Entrenando modelo de Árbol de Decisión...")

    modelo = DecisionTreeClassifier(max_depth=4, random_state=42)
    modelo.fit(X_train, y_train)

    print("\n=== Evaluación del Modelo ===")
    y_pred = modelo.predict(X_test)

    print(classification_report(y_test, y_pred, zero_division=0))

    # -----------------------------------------------------
    # 4. Predicción final + clasificación de riesgo
    # -----------------------------------------------------
    prob_activo = modelo.predict_proba(X)[:, 1]
    clientes["probabilidad_activo"] = prob_activo
    clientes["probabilidad_abandono"] = 1 - prob_activo

    clientes["nivel_riesgo"] = clientes["probabilidad_abandono"].apply(clasificar_riesgo)

    clientes_riesgo = clientes[clientes["nivel_riesgo"] == "Alto riesgo"]
    print(f"\nClientes en alto riesgo: {len(clientes_riesgo)}")

    # Exportar resultados
    salida = clientes[
        [
            "user",
            "mensajes",
            "dias_desde_ultimo",
            "estado",
            "probabilidad_activo",
            "probabilidad_abandono",
            "nivel_riesgo",
        ]
    ]

    salida.to_csv(FINAL_PATH / "clientes_predicciones.csv",
                  index=False,
                  encoding="utf-8-sig",
                  sep=";")

    print(f"\nArchivo generado: {FINAL_PATH / 'clientes_predicciones.csv'}")

    # -----------------------------------------------------
    # 5. Sistema de recomendación (omitido)
    # -----------------------------------------------------
    print("\n[SISTEMA DE RECOMENDACIÓN]")
    print("No hay matriz cliente-producto disponible. Se omite similitud.")
    similaridad_df = None

    # -----------------------------------------------------
    # 6. Alertas automáticas
    # -----------------------------------------------------
    print("\n=== ALERTAS AUTOMÁTICAS ===")

    if not clientes_riesgo.empty:
        print(f"{len(clientes_riesgo)} clientes requieren contacto inmediato:\n")
        for i, row in clientes_riesgo.head(5).iterrows():
            print(
                f"Cliente: {row['user']} | "
                f"Prob. Abandono: {row['probabilidad_abandono']:.2f} | "
                f"Días sin actividad: {row['dias_desde_ultimo']} | "
                f"Acción sugerida: Enviar mensaje de seguimiento."
            )
    else:
        print("No hay clientes en alto riesgo.")

    return salida, similaridad_df


# ---------------------------------------------------------
# Ejecución de prueba
# ---------------------------------------------------------
if __name__ == "__main__":
    print("--- Prueba del módulo de predicción ---")
    try:
        run_prediction_model()
    except Exception as e:
        print(f"❌ Error en ejecución: {e}")
