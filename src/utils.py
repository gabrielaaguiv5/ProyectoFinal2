{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyMPGSxXw6b9eb5Sho1Vugmi",
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
        "<a href=\"https://colab.research.google.com/github/gabrielaaguiv5/ProyectoFinal2/blob/main/src/utils.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "-ia8lXPgcbqb"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "utils.py\n",
        "Funciones auxiliares de soporte para SmartChat Insight.\n",
        "\"\"\"\n",
        "\n",
        "import os\n",
        "from datetime import datetime\n",
        "\n",
        "def log(message: str):\n",
        "    \"\"\"\n",
        "    Imprime mensajes de log con timestamp.\n",
        "    \"\"\"\n",
        "    time = datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")\n",
        "    print(f\"[{time}] {message}\")\n",
        "\n",
        "\n",
        "def ensure_directories(paths):\n",
        "    \"\"\"\n",
        "    Crea carpetas si no existen.\n",
        "    \"\"\"\n",
        "    for p in paths:\n",
        "        os.makedirs(p, exist_ok=True)\n",
        "\n",
        "\n",
        "def get_chat_files(folder_path):\n",
        "    \"\"\"\n",
        "    Retorna la lista de archivos .txt en la carpeta especificada.\n",
        "    \"\"\"\n",
        "    return [f for f in os.listdir(folder_path) if f.endswith(\".txt\")]\n"
      ]
    }
  ]
}