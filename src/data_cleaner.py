# =========================================================
#  SmartChat Insight - Limpieza y estructuración de WhatsApp
# =========================================================

import sys
import codecs
# Forzar salida en UTF-8 en Windows
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "replace")

import re
import pandas as pd
from pathlib import Path
from datetime import datetime


# =========================================================
#   🔧 RUTAS RELATIVAS UNIVERSALES
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_PATH   = BASE_DIR / "data" / "raw_chats"
CLEAN_PATH = BASE_DIR / "data" / "cleaned"

# Crear carpetas si no existen
RAW_PATH.mkdir(parents=True, exist_ok=True)
CLEAN_PATH.mkdir(parents=True, exist_ok=True)


# =========================================================
#   🔍 REGEX UNIVERSAL PARA WHATSAPP
# =========================================================
WHATSAPP_PATTERN = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}(?:\s?[ap]\.?m\.?)?) - (.*?): (.*)$",
    re.IGNORECASE
)


# =========================================================
#   🔧 PARSEO DE FECHA
# =========================================================
def parse_date(date_str: str):
    formatos = [
        "%d/%m/%Y",
        "%d/%m/%y",
    ]

    for fmt in formatos:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return pd.NaT


# =========================================================
#   🔧 PARSEO DE HORA
# =========================================================
def parse_time(time_str: str):
    time_str = time_str.lower().replace(" ", "")
    time_str = time_str.replace("a.m.", "am").replace("p.m.", "pm")

    formatos = ["%I:%M%p", "%H:%M"]

    for fmt in formatos:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue

    return None


# =========================================================
#   📥 CONVERTIR ARCHIVO WHATSAPP A DATAFRAME
# =========================================================
def db_whatsapp_chat(file_path: Path) -> pd.DataFrame:
    data = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                match = WHATSAPP_PATTERN.match(line)

                if match:
                    raw_date, raw_time, user, message = match.groups()

                    date = parse_date(raw_date)
                    time = parse_time(raw_time)

                    data.append([date, time, user.strip(), message.strip()])

        return pd.DataFrame(data, columns=["date", "time", "user", "message"])

    except Exception as e:
        print(f"❌ ERROR al procesar {file_path.name}: {e}")
        return pd.DataFrame()


# =========================================================
#   🚀 EJECUCIÓN DEL PIPELINE COMPLETO
# =========================================================
def run_data_cleaning(output_filename="whatsapp_clean.csv") -> pd.DataFrame:
    print("\n[FASE DE LIMPIEZA] Iniciando proceso de estructuración de chats...")

    all_chats = []

    # Leer archivos desde data/raw_chats
    for file in RAW_PATH.glob("*.txt"):
        print(f"📄 Procesando: {file.name}")
        df_chat = db_whatsapp_chat(file)

        if not df_chat.empty:
            df_chat["file_name"] = file.name
            all_chats.append(df_chat)

    if not all_chats:
        print("⚠️ No se encontraron archivos .txt válidos para procesar.")
        return pd.DataFrame()

    df_all = pd.concat(all_chats, ignore_index=True)

    # Remover mensajes de sistema
    df_all = df_all[
        ~df_all["message"].str.contains("cifrados de extremo a extremo", na=False)
    ]

    # Remover fechas inválidas
    df_all.dropna(subset=["date"], inplace=True)

    # Guardar archivo limpio
    output_file = CLEAN_PATH / output_filename
    df_all.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("-" * 50)
    print(f"✅ Archivo limpio guardado en: {output_file.resolve()}")
    print(f"📊 Total de mensajes procesados: {len(df_all)}")
    print("-" * 50)

    return df_all


# =========================================================
#   ▶️ PUNTO DE ENTRADA
# =========================================================
if __name__ == "__main__":
    run_data_cleaning()
