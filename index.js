require('dotenv').config(); 

// --- 1. IMPORTACIONES ---
const express = require('express');
const qrcodeLib = require('qrcode'); 
const { Client, LocalAuth } = require('whatsapp-web.js'); // Cambiado a LocalAuth
const mongoose = require('mongoose');
const qrcode = require('qrcode-terminal');
const { createClient } = require('@supabase/supabase-js');
const path = require('path');

// --- 2. CONFIGURACIÓN DE VARIABLES ---
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
const MONGO_URI = process.env.MONGO_URI;
const SUPABASE_BUCKET_NAME = 'qr-sessions'; 

if (!SUPABASE_URL || !SUPABASE_KEY) {
    console.error('\n❌ ERROR: Faltan variables de Supabase.');
    process.exit(1);
}

// --- 3. HEALTH CHECK PARA RAILWAY ---
const app = express();
const port = process.env.PORT || 3000;
app.get('/', (req, res) => res.status(200).send('Bot is Online'));
app.listen(port, '0.0.0.0', () => console.log(`[HEALTH CHECK] Port ${port}`));

// --- 4. INICIALIZACIÓN DEL CLIENTE ---
// Usamos LocalAuth porque tienes un volumen montado en /app/.wwebjs_auth
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: 'session',
        dataPath: path.join(__dirname, '.wwebjs_auth') // Apunta directamente al volumen
    }),
    webVersionCache: {
        type: 'remote',
        remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2412.54.html',
    },
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--no-zygote'
        ]
    }
});

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// --- 5. MANEJO DE EVENTOS ---

client.on('qr', async (qr) => {
    console.log('📱 NUEVO QR GENERADO:');
    if (!process.env.RAILWAY_ENVIRONMENT) {
        qrcode.generate(qr, { small: true });
    }

    try {
        const qrBuffer = await qrcodeLib.toBuffer(qr, { type: 'png' });
        const fileName = `temp-qr/session-${Date.now()}.png`;
        await supabase.storage.from(SUPABASE_BUCKET_NAME).upload(fileName, qrBuffer, {
            contentType: 'image/png',
            upsert: true
        });
        const { data } = supabase.storage.from(SUPABASE_BUCKET_NAME).getPublicUrl(fileName);
        console.log(`➡️ ESCANEA AQUÍ: ${data.publicUrl}`);
    } catch (e) {
        console.error('❌ Error Supabase QR:', e.message);
    }
});

client.on('ready', () => {
    console.log('✅ BOT LISTO Y CONECTADO.');
    console.log('📂 Sesión guardada en el volumen persistente.');
});

client.on('message', async (msg) => {
    if (msg.from.includes('@g.us') || msg.from.includes('broadcast')) return;

    const telefonoCliente = msg.from.replace('@c.us', '');
    
    try {
        // Guardar en Supabase (Opcional si usas DB)
        await supabase.from('mensajes_whatsapp').insert([{ 
            telefono_origen: telefonoCliente, 
            mensaje_texto: msg.body, 
            direccion: 'entrada' 
        }]);

        if (msg.body.toLowerCase().includes('hola')) {
            await msg.reply('¡Hola! Soy tu asistente virtual trabajando desde el Volumen de Railway.');
        }
    } catch (error) {
        console.error("❌ Error Supabase:", error.message);
    }
});

// Conectar a Mongo solo para tus datos de mensajes (opcional)
if (MONGO_URI) {
    mongoose.connect(MONGO_URI)
        .then(() => console.log('✅ Conectado a MongoDB (Solo para datos)'))
        .catch(err => console.error('⚠️ Error Mongo:', err.message));
}

console.log('🚀 Inicializando WhatsApp...');
client.initialize();