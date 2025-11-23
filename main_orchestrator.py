# main_orchestrator.py

# Importamos la función desde el módulo src.data.loader
from src.data.loader import obtener_datos_whatsapp
# from src.analysis import analysis_function  # Futura importación de análisis

print("--- ORQUESTADOR INICIADO ---")

# 1. ETAPA: EXTRACCIÓN Y LIMPIEZA INICIAL (Supabase)
df_mensajes = obtener_datos_whatsapp()

if not df_mensajes.empty:
    print("\n--- ETAPA 1: DATOS CARGADOS CORRECTAMENTE ---")
    print("Columnas y tipos de datos del DataFrame:")
    df_mensajes.info()
    print("\nPrimeros 5 registros:")
    print(df_mensajes.head())
    
    # 2. ETAPA: TRANSFORMACIÓN / ANÁLISIS (aquí se llamaría a src.analysis)
    # print("\n--- ETAPA 2: REALIZANDO ANÁLISIS ---")
    # df_metricas = analysis_function(df_mensajes)
    
    # 3. ETAPA: CARGA (aquí se guardaría el CSV final o se conectaría a Power BI)
    # print("\n--- ETAPA 3: GENERACIÓN DE SALIDA ---")
    
else:
    print("\n--- ¡FALLO! No se pudieron cargar datos desde Supabase. Revisar credenciales o permisos. ---")


print("--- ORQUESTADOR FINALIZADO ---")