# =========================================================
# ORQUESTADOR DEL PROYECTO
# Ejecuta: data_cleaner -> analysis_and_export -> prediction_model
# =========================================================

import subprocess
import sys
from pathlib import Path

# -------------------------------------------------------------------
# RUTA BASE - carpeta /src donde está el orquestador
# -------------------------------------------------------------------
SRC_PATH = Path(__file__).resolve().parent

MODULES = [
    ("DATA CLEANER", SRC_PATH / "data_cleaner.py"),
    ("ANÁLISIS Y EXPORTACIÓN", SRC_PATH / "analysis_and_export.py"),
    ("PREDICCIÓN Y RECOMENDACIÓN", SRC_PATH / "prediction_model.py"),
]

# -------------------------------------------------------------------
# FUNCIÓN PARA EJECUTAR UN MÓDULO PY
# -------------------------------------------------------------------


def run_step(name: str, file_path: Path):
    print("\n==============================")
    print(f"➡️  Ejecutando módulo: {name}")
    print("==============================")

    if not file_path.exists():
        print(f"❌ ERROR: No existe el archivo {file_path}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(file_path)],
            cwd=SRC_PATH,
            capture_output=True,
            text=True,
            encoding="utf-8",     # <-- 🔥 CLAVE PARA EVITAR ERRORES UNICODE
            errors="replace"      # <-- Reemplaza caracteres no soportados
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("⚠️ ERRORES:\n", result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error ejecutando {name}: {e}")
        return False


# -------------------------------------------------------------------
# EJECUCIÓN SECUENCIAL DE LOS MÓDULOS
# -------------------------------------------------------------------
def main():
    print("🚀 Iniciando orquestador...\n")
    print(f"📁 SRC: {SRC_PATH}\n")

    for name, path in MODULES:
        ok = run_step(name, path)
        if not ok:
            print(f"\n❌ El proceso '{name}' falló. Deteniendo orquestador.")
            break
    else:
        print("\n✅ ORQUESTACIÓN COMPLETADA CON ÉXITO")


if __name__ == "__main__":
    main()
