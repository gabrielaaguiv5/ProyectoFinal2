# SmartChat Insight  
### Convierte tus conversaciones de WhatsApp en inteligencia comercial

**SmartChat Insight** es un proyecto desarrollado en **Python** y **Power BI** que transforma los chats exportados desde WhatsApp en información útil para la toma de decisiones comerciales.  
Permite identificar **clientes recurrentes**, **clientes perdidos**, **productos más vendidos** y **patrones de comunicación**, generando métricas claras y dashboards interactivos.

---

## Objetivo del Proyecto
El objetivo es procesar automáticamente los archivos `.txt` descargados desde WhatsApp, limpiar y estructurar los datos, analizarlos con **Python** y visualizarlos en **Power BI**, ayudando a los emprendedores a conocer mejor a sus clientes y optimizar sus ventas.

---

## Fases del Proyecto

### **Fase 1: Extracción de Datos**
- Exporta tus conversaciones desde WhatsApp usando la opción **“Exportar chat” → “Sin archivos multimedia”**.  
- Los archivos `.txt` obtenidos se guardan en:

  /data/raw_chats/

- Cada archivo corresponde a una compilación de chats del negocio.

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

### **Fase 4: Visualización en Power BI**
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
# Fase 5: Documentación y Publicación

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
  │   ├── 01_cleaning.ipynb       # Limpieza y estructuración de los chats
  │   ├── 02_analysis.ipynb       # Análisis de clientes y productos
  │   └── 03_export_powerbi.ipynb # Exportación a Power BI
  │
  ├── src/
  │   ├── preprocessing.py        # Funciones de limpieza y extracción
  │   ├── analytics.py            # Funciones de análisis y segmentación
  │   └── utils.py                # Funciones auxiliares
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

