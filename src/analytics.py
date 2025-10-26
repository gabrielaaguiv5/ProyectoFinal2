{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyOBCNgQKHNIjLxkmSN0QmXL",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/gabrielaaguiv5/ProyectoFinal2/blob/main/src/analytics.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "UrULNIT-b9vm"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "analytics.py\n",
        "Funciones de análisis de clientes y detección de productos.\n",
        "\"\"\"\n",
        "\n",
        "import pandas as pd\n",
        "import re\n",
        "from datetime import datetime\n",
        "\n",
        "def classify_client(dias):\n",
        "    \"\"\"\n",
        "    Clasifica un cliente según días desde último contacto.\n",
        "    \"\"\"\n",
        "    if dias <= 15:\n",
        "        return \"Frecuente\"\n",
        "    elif dias <= 45:\n",
        "        return \"Inactivo reciente\"\n",
        "    else:\n",
        "        return \"Perdido\"\n",
        "\n",
        "\n",
        "def analyze_clients(df: pd.DataFrame):\n",
        "    \"\"\"\n",
        "    Genera métricas de clientes: mensajes, fechas y estado.\n",
        "    \"\"\"\n",
        "    df[\"date\"] = pd.to_datetime(df[\"date\"], errors=\"coerce\")\n",
        "\n",
        "    activity = (\n",
        "        df.groupby(\"user\")\n",
        "          .agg(\n",
        "              mensajes=(\"message\", \"count\"),\n",
        "              primer_contacto=(\"date\", \"min\"),\n",
        "              ultimo_contacto=(\"date\", \"max\")\n",
        "          )\n",
        "          .reset_index()\n",
        "    )\n",
        "\n",
        "    max_date = df[\"date\"].max()\n",
        "    activity[\"dias_desde_ultimo\"] = (max_date - activity[\"ultimo_contacto\"]).dt.days\n",
        "    activity[\"estado\"] = activity[\"dias_desde_ultimo\"].apply(classify_client)\n",
        "\n",
        "    return activity\n",
        "\n",
        "\n",
        "def analyze_products(df: pd.DataFrame, keywords=None):\n",
        "    \"\"\"\n",
        "    Detecta productos o servicios mencionados en los mensajes.\n",
        "    \"\"\"\n",
        "    if keywords is None:\n",
        "        keywords = [\"vidrio\", \"fachada\", \"aluminio\", \"puerta\", \"ventana\",\n",
        "                    \"baño\", \"división\", \"pasamanos\", \"pérgola\", \"instalador\"]\n",
        "\n",
        "    conteo = {}\n",
        "    for word in keywords:\n",
        "        conteo[word] = df[\"message\"].str.contains(word, case=False, na=False).sum()\n",
        "\n",
        "    df_productos = pd.DataFrame(list(conteo.items()), columns=[\"producto\", \"menciones\"])\n",
        "    df_productos = df_productos.sort_values(by=\"menciones\", ascending=False)\n",
        "    return df_productos\n",
        "\n",
        "\n",
        "def export_analysis(activity, products, output_path=\"data/outputs/\"):\n",
        "    \"\"\"\n",
        "    Exporta los resultados de análisis a CSV.\n",
        "    \"\"\"\n",
        "    path = Path(output_path)\n",
        "    path.mkdir(parents=True, exist_ok=True)\n",
        "    activity.to_csv(path / \"clientes.csv\", index=False, encoding=\"utf-8-sig\")\n",
        "    products.to_csv(path / \"productos.csv\", index=False, encoding=\"utf-8-sig\")\n",
        "    print(\"✅ Archivos exportados a carpeta outputs/\")\n"
      ]
    }
  ]
}