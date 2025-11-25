# SmartChat Insight  
### Convierte tus conversaciones de WhatsApp en inteligencia comercial

**SmartChat Insight** es un proyecto desarrollado en **Python** y **Power BI** que transforma los chats exportados desde WhatsApp en información útil para la toma de decisiones comerciales.  
SmartChat Insight es una plataforma diseñada para transformar chats de WhatsApp en datos estructurados, métricas comerciales, modelos predictivos y dashboards interactivos.
El proyecto combina Python, Supabase, Power BI y un orquestador automático que ejecuta el flujo completo:

1. Limpieza y estructuración de chats
2. Análisis comercial
3. Exportación a Power BI
4. Reglas inteligentes de recomendación y churn
5. Acciones sugeridas para cada cliente

---

## ¿Qué hace SmartChat Insight?
A partir de las conversaciones exportadas desde WhatsApp (o recibidas desde un servidor Supabase), el sistema:

- Identifica clientes frecuentes, inactivos, nuevos o perdidos
- Detecta patrones de compra y menciones de productos
- Calcula métricas de actividad, frecuencia y conversiones
- Genera recomendaciones automáticas para retención y ventas
- Produce mensajes sugeridos listos para enviar
- Exporta datos limpios para Power BI
- Ejecuta todo el pipeline con un orquestador secuencia

---
## Arquitectura del Proyecto
El proyecto se ejecuta mediante un orquestador Python, encargado de lanzar cada módulo en orden:

data_cleaner.py → analysis_and_export.py → prediction_model.py

Cada fase deja resultados ordenados en la carpeta /data/ y el orquestador valida errores, imprime logs y asegura ejecución consistente


---
## Fases del Proyecto

### **Fase 1: Extracción de Datos (WhatsApp + Supabase)**
- SmartChat Insight puede obtener los chats desde dos fuentes:

1. Archivos .txt exportados desde WhatsApp

WhatsApp → Exportar chat → Sin archivos multimedia

Guardar los .txt en:
/data/raw_chats/

2. Servidor Supabase

También es posible almacenar o sincronizar los chats en una tabla Supabase y descargarlos desde allí para ser procesados automáticamente.

Esto permite tener un backend centralizado, histórico y accesible para múltiples usuarios o dispositivos.

---

### **Fase 2: Limpieza y Preprocesamiento (Python + Pandas)**
- Se extraen y estructuran los mensajes utilizando expresiones regulares (`re`):
- Fecha y hora  
- Usuario o remitente  
- Mensaje enviado  
- Se eliminan mensajes de sistema, líneas vacías y texto irrelevante.  
- Se genera un DataFrame estructurado con formato:

  date | time | user | message

- Resultado exportado a:

  /data/cleaned/whatsapp_clean.csv

---

### **Fase 3: Análisis de Clientes y Productos**
- Agrupación de mensajes por usuario para identificar:
- 🟢 Clientes frecuentes  
- 🟡 Clientes nuevos  
- 🔴 Clientes inactivos  
- Búsqueda de **productos o servicios mencionados** mediante palabras clave.  
- Cálculo de métricas clave:
- Volumen de mensajes por usuario  
- Último contacto  
- Frecuencia promedio  
- Productos más solicitados  

Resultados guardados en:

  /data/outputs/clientes.csv
  /data/outputs/productos.csv
  /data/outputs/actividad.csv


---

### **Fase 4: Predicción y Recomendación**
Reglas inteligentes basadas en estado del cliente:

| Estado            | Acción         | Prob. conversión | Días |
| ----------------- | -------------- | ---------------- | ---- |
| Frecuente         | Mantener flujo | 0.75             | 7    |
| Inactivo reciente | Seguimiento    | 0.45             | 2    |
| Perdido           | Reactivación   | 0.18             | 1    |
| Nuevo             | Bienvenida     | 0.90             | 0    |


También genera:
- Fecha recomendada de contacto
- Mensaje sugerido para enviar
---

### **Fase 5: Visualización en Power BI**
- Importación de los archivos CSV limpios a **Power BI Desktop**.  
- Creación de dashboards con indicadores clave:
  - Clientes activos e inactivos  
  - Tendencias de conversación por período  
  - Productos o servicios más solicitados  
  - Tasa de recompra o recontacto  
- Uso de medidas DAX para generar KPIs dinámicos:
  ```DAX
  Clientes Activos = COUNTROWS(FILTER(Clientes, Clientes[estado] = "Frecuente"))
---
# Fase 6: Documentación y Publicación

### El código, los notebooks y los datos limpios se organizan dentro de un repositorio GitHub.
- Se documentan las dependencias en requirements.txt.
- Este README.md explica cómo replicar el flujo completo del proyecto.

### Estructura del Repositorio
```

  ├── data/
  │   ├── raw_chats/              # Archivos .txt exportados desde WhatsApp
  │   ├── cleaned/                # Datos procesados
  │   └── outputs/                # Archivos finales (clientes, productos, actividad)
  │
  ├── notebooks/
  │   ├──
  ├── src/
  │   ├── data_cleaner.py
  │   ├── analysis_and_export.py
  │   ├── analysis_and_export.py
  │   └── orchestrator.py               
  │
  ├── dashboard/
  │   └── smartchat_dashboard.pbix   # Dashboard en Power BI
  │
  ├── requirements.txt            # Dependencias del proyecto
  ├── .gitignore                  # Archivos y carpetas a ignorar (ej. datos sensibles)
  └── README.md                   # Documentación principal del proyect
```

### Ejecución del Proyecto
- Clona este repositorio:
- Instala las dependencias:
- Coloca tus archivos .txt de WhatsApp en:
- Ejecuta los notebooks en orden:
    - notebooks/01_cleaning.ipynb
    - notebooks/02_analysis.ipynb
    - notebooks/03_export_powerbi.ipynb
 - Abre dashboard/smartchat_dashboard.pbix en Power BI Desktop y conéctalo a los CSV exportados
---
# Privacidad y Cumplimiento Legal

- Solo se procesan chats exportados voluntariamente por el usuario.
- No se accede automáticamente a cuentas de WhatsApp ni a APIs externas.
- Cumple con la Ley 1581 de 2012 de protección de datos personales (Colombia).
- Los datos sensibles o privados deben excluirse del repositorio (.gitignore).
---
# Conclusión

SmartChat Insight demuestra cómo un negocio puede aprovechar sus propias conversaciones de WhatsApp para generar inteligencia comercial.
Este proyecto es escalable, reproducible y adaptable a cualquier tipo de negocio que gestione clientes mediante chat.

