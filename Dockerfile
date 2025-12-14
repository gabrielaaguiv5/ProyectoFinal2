# Usa una imagen base de Node.js, la versión slim es ligera y buena para producción
FROM node:20-slim

# Evita que Chrome intente usar sandboxing que es problemático en entornos Docker
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable

# Crea el directorio de trabajo
WORKDIR /app

# Instala Google Chrome y las dependencias de sistema CRÍTICAS para Puppeteer
# Esto incluye las librerías necesarias para libgobject-2.0.so.0 y otros
RUN apt-get update && apt-get install -y \
    # Dependencias de Puppeteer y W-Web.js
    curl \
    gnupg \
    libnss3 \
    libgconf-2-4 \
    libasound2 \
    libxss1 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    libglib2.0-0 \
    libxtst6 \
    # Google Chrome Stable para Puppeteer
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-archive-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Limpieza
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de definición de dependencias
COPY package*.json ./

# Instala las dependencias de Node (incluyendo express, qrcode, wwebjs-mongo)
# Este paso es CRÍTICO para que el nuevo código de estabilidad funcione
RUN npm install

# Copia el resto del código (index.js, .env, etc.)
COPY . .

# Expone el puerto que usa Express para el Health Check (generalmente 3000)
# Aunque Railway maneja la asignación, es buena práctica para Docker
EXPOSE 3000

# Comando de inicio
CMD [ "node", "index.js" ]