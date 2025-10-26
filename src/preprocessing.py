{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyNBFWw4co5aYazuL0ZpNBvg",
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
        "<a href=\"https://colab.research.google.com/github/gabrielaaguiv5/ProyectoFinal2/blob/main/src/preprocessing.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "uYk_krwScHHh"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "preprocessing.py\n",
        "Funciones para leer, limpiar y estructurar archivos .txt exportados de WhatsApp.\n",
        "\"\"\"\n",
        "\n",
        "import re\n",
        "import pandas as pd\n",
        "from pathlib import Path\n",
        "\n",
        "def parse_whatsapp_chat(file_path):\n",
        "    \"\"\"\n",
        "    Convierte un archivo .txt exportado de WhatsApp en un DataFrame estructurado.\n",
        "    Retorna columnas: date, time, user, message\n",
        "    \"\"\"\n",
        "    pattern = re.compile(r\"^(\\d{1,2}/\\d{1,2}/\\d{2,4}), (\\d{1,2}:\\d{2}\\s?[ap]\\.?\\s?m\\.?) - (.*?): (.*)\")\n",
        "    data = []\n",
        "\n",
        "    with open(file_path, encoding=\"utf-8\") as f:\n",
        "        for line in f:\n",
        "            line = line.strip()\n",
        "            match = pattern.match(line)\n",
        "            if match:\n",
        "                date, time, user, message = match.groups()\n",
        "                data.append([date, time, user.strip(), message.strip()])\n",
        "\n",
        "    df = pd.DataFrame(data, columns=[\"date\", \"time\", \"user\", \"message\"])\n",
        "    return df\n",
        "\n",
        "\n",
        "def clean_all_chats(raw_folder: str, output_file: str):\n",
        "    \"\"\"\n",
        "    Procesa todos los archivos .txt de una carpeta y genera un CSV limpio.\n",
        "    \"\"\"\n",
        "    raw_path = Path(raw_folder)\n",
        "    chats = []\n",
        "\n",
        "    for file in raw_path.glob(\"*.txt\"):\n",
        "        print(f\"Procesando {file.name}...\")\n",
        "        df_chat = parse_whatsapp_chat(file)\n",
        "        df_chat[\"file_name\"] = file.name\n",
        "        chats.append(df_chat)\n",
        "\n",
        "    df_all = pd.concat(chats, ignore_index=True)\n",
        "\n",
        "    # Eliminar mensajes del sistema\n",
        "    df_all = df_all[~df_all[\"message\"].str.contains(\"cifrados de extremo a extremo\", na=False)]\n",
        "\n",
        "    # Normalizar fechas\n",
        "    df_all[\"date\"] = pd.to_datetime(df_all[\"date\"], dayfirst=True, errors=\"coerce\")\n",
        "\n",
        "    df_all.to_csv(output_file, index=False, encoding=\"utf-8-sig\")\n",
        "    print(f\"✅ Archivo limpio guardado en: {output_file}\")\n",
        "    return df_all\n"
      ]
    }
  ]
}