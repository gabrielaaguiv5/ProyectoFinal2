import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv() 

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def obtener_datos_whatsapp() -> pd.DataFrame:
    """
    Se conecta a Supabase y trae todos los mensajes de la tabla 'mensajes_whatsapp'.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Las credenciales de Supabase no están configuradas en .env.")
        return pd.DataFrame()
        
    try:
        print("Conectando a Supabase y cargando datos...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Consulta a la tabla mensajes_whatsapp
        # Usamos el cliente para ejecutar la consulta y obtener el resultado completo.
        result = supabase.from("mensajes_whatsapp").select("*").execute()
        
        # 1. Verificar si hay un error en la respuesta
        if result.error:
            print(f"❌ Error Supabase al consultar: {result.error.message}")
            return pd.DataFrame()

        # 2. Asignar los datos
        data = result.data
        
        if not data:
            print("Advertencia: La tabla está vacía o no tiene permisos de lectura.")
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Conversión de tipos de datos (esencial para análisis)
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
             
        print(f"✅ Éxito: Se cargaron {len(df)} registros desde Supabase.")
        return df

    except Exception as e:
        print(f"❌ Error crítico al conectar o leer: {e}")
        return pd.DataFrame()