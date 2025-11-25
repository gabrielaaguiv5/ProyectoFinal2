# =========================================================
#  SmartChat Insight
#  Módulo de Predicción y Recomendación (Churn y Similitud)
# =========================================================

import sys
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime

# Forzar UTF-8 en Windows para evitar errores con emojis
sys.stdout.reconfigure(encoding="utf-8")

# ===========================
# Rutas relativas universales
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent
FINAL_PATH = BASE_DIR / "data" / "outputs" / "final"


# =========================================================
# Carga de datos
# =========================================================

def cargar_archivos():
    print("Cargando archivos finales...")

    clientes = pd.read_csv(FINAL_PATH / "clientes_powerbi.csv", sep=";")
    clientes_final = pd.read_csv(
        FINAL_PATH / "clientes_final_powerbi.csv", sep=";")
    productos = pd.read_csv(FINAL_PATH / "productos_powerbi.csv", sep=";")
    resumen = pd.read_csv(FINAL_PATH / "resumen_clientes.csv", sep=";")

    print("Archivos cargados correctamente")
    return clientes, clientes_final, productos, resumen


# =========================================================
# Procesamiento de fechas y reglas
# =========================================================

REGLAS_BASE = {
    "Frecuente": {"accion": "Mantener flujo de comunicación", "probabilidad_conversion": 0.75, "dias_para_contactar": 7},
    "Inactivo reciente": {"accion": "Mensaje de seguimiento", "probabilidad_conversion": 0.45, "dias_para_contactar": 2},
    "Perdido": {"accion": "Campaña de reactivación", "probabilidad_conversion": 0.18, "dias_para_contactar": 1},
}


def preparar_clientes(clientes_final):
    print("Procesando columnas de fechas y reglas...")

    for col in ["primer_contacto", "ultimo_contacto"]:
        clientes_final[col] = pd.to_datetime(
            clientes_final[col], errors="ignore")

    fecha_corte = clientes_final["ultimo_contacto"].max().date()
    print(f"Fecha de corte: {fecha_corte}")

    # Cliente nuevo (últimos 3 días)
    clientes_final["nuevo"] = clientes_final["primer_contacto"] >= (
        pd.to_datetime(fecha_corte) - pd.Timedelta(days=3)
    )
    clientes_final.loc[clientes_final["nuevo"], "estado"] = "Nuevo"

    # Combinar reglas
    reglas = REGLAS_BASE.copy()
    reglas["Nuevo"] = {
        "accion": "Mensaje de bienvenida",
        "probabilidad_conversion": 0.90,
        "dias_para_contactar": 0
    }

    return clientes_final, reglas


# =========================================================
# Lógica del modelo de recomendación
# =========================================================

def recomendar(row, reglas):
    estado = row["estado"]
    ultimo = row["ultimo_contacto"]
    hoy = datetime.today().date()

    regla = reglas.get(estado)
    if not regla:
        return pd.Series({
            "accion_recomendada": "Revisar",
            "dias_para_contactar": np.nan,
            "fecha_recomendada_contacto": None
        })

    return pd.Series({
        "accion_recomendada": regla["accion"],
        "dias_para_contactar": regla["dias_para_contactar"],
        "fecha_recomendada_contacto": (hoy + pd.Timedelta(days=regla["dias_para_contactar"])).date()
    })


def generar_mensaje(row):
    estado = row["estado"]
    nombre = row["user"]

    mensajes = {
        "Frecuente": f"Hola {nombre}, gracias por mantener el contacto 😊. ¿En qué podemos ayudarte hoy?",
        "Inactivo reciente": f"Hola {nombre}, hace unos días no conversamos. ¿Te sigo ayudando con tu pedido?",
        "Perdido": f"Hola {nombre}, tenemos novedades y promociones disponibles para ti. ¿Deseas verlas?",
        "Nuevo": f"¡Bienvenido {nombre}! Gracias por escribirnos 😊. ¿En qué podemos ayudarte hoy?",
    }

    return mensajes.get(estado, "Hola, ¿cómo podemos ayudarte?")


# =========================================================
# Pipeline principal (usado por el orquestador)
# =========================================================

def procesar_recomendaciones():
    print("\nIniciando módulo: Predicción y Recomendación...")

    # 1. Cargar datos
    _, clientes_final, _, _ = cargar_archivos()

    # 2. Procesar estructura
    clientes_final, reglas = preparar_clientes(clientes_final)

    # 3. Generar recomendaciones
    print("Generando acciones recomendadas...")
    reco = clientes_final.apply(lambda r: recomendar(r, reglas), axis=1)
    clientes_final = pd.concat([clientes_final, reco], axis=1)

    # Mensajes personalizados
    clientes_final["mensaje_sugerido"] = clientes_final.apply(
        generar_mensaje, axis=1)

    # Exportar
    output_path = FINAL_PATH / "acciones_recomendadas.csv"
    clientes_final.to_csv(output_path, index=False, sep=";")

    print(f"Archivo exportado: {output_path}")
    print("Módulo completado.\n")

    return clientes_final


# =========================================================
# Ejecución independiente (llamado por el orquestador)
# =========================================================

if __name__ == "__main__":
    procesar_recomendaciones()
