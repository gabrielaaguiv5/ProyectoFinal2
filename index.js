require('dotenv').config(); 

// --- 1. IMPORTACIONES ---
const express = require('express');
const qrcodeLib = require('qrcode'); 
const { Client, RemoteAuth } = require('whatsapp-web.js');
const { MongoStore } = require('wwebjs-mongo');
const mongoose = require('mongoose');
const qrcode = require('qrcode-terminal');
const { createClient } = require('@supabase/supabase-js');

// --- 2. CONFIGURACIÓN DE VARIABLES ---
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
const MONGO_URI = process.env.MONGO_URI;
const SUPABASE_BUCKET_NAME = 'qr-sessions'; 

if (!SUPABASE_URL || !SUPABASE_KEY || !MONGO_URI) {
    console.error('\n❌ ERROR: Faltan variables de entorno (SUPABASE_URL, SUPABASE_KEY, MONGO_URI).');
    process.exit(1);
}

// --- 3. HEALTH CHECK (Para que Railway sepa que el bot vive) ---
const app = express();
const port = process.env.PORT || 3000;
app.get('/', (req, res) => res.status(200).send('Bot is Online'));
app.listen(port, () => console.log(`[HEALTH CHECK] Port ${port}`));

// --- 4. CONEXIÓN A MONGODB Y ARRANQUE ---
mongoose.connect(MONGO_URI).then(() => {
    console.log('✅ Conectado a MongoDB');
    
    const store = new MongoStore({ mongoose: mongoose });
    
    const client = new Client({
        authStrategy: new RemoteAuth({
            store: store,
            backupSyncIntervalMs: 60000,
            dataPath: './.wwebjs_auth' 
        }),
        puppeteer: {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--no-zygote'
            ]
        }
    });

    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

    // --- MANEJO DEL QR ---
    client.on('qr', async (qr) => {
        console.log('📱 Nuevo QR generado.');
        
        // Solo mostrar QR en terminal si NO estamos en Railway (para no ensuciar logs)
        if (!process.env.RAILWAY_ENVIRONMENT) {
            qrcode.generate(qr, { small: true });
        }

        try {
            const qrBuffer = await qrcodeLib.toBuffer(qr, { type: 'png' });
            const path = `temp-qr/session-${Date.now()}.png`;
            await supabase.storage.from(SUPABASE_BUCKET_NAME).upload(path, qrBuffer, {
                contentType: 'image/png',
                upsert: true
            });
            const { data } = supabase.storage.from(SUPABASE_BUCKET_NAME).getPublicUrl(path);
            console.log(`➡️ Escanea aquí: ${data.publicUrl}`);
        } catch (e) {
            console.error('❌ Error subiendo QR a Supabase:', e.message);
        }
    });

    client.on('ready', () => console.log('✅ BOT LISTO Y CONECTADO.'));
    
    client.on('remote_session_saved', () => {
        console.log('💾 Sesión guardada en MongoDB con éxito.');
    });

    // --- LÓGICA DE MENSAJES ---
    client.on('message', async (msg) => {
        if (msg.from.includes('@g.us') || msg.from.includes('broadcast')) return;

        const telefonoCliente = msg.from.replace('@c.us', '');
        
        try {
            // Guardar entrada
            await supabase.from('mensajes_whatsapp').insert([{ 
                telefono_origen: telefonoCliente, 
                mensaje_texto: msg.body, 
                direccion: 'entrada' 
            }]);

            if (msg.body.toLowerCase().includes('hola')) {
                const saludo = '¡Hola! Soy tu asistente virtual.';
                await msg.reply(saludo);
                await supabase.from('mensajes_whatsapp').insert([{ 
                    telefono_origen: telefonoCliente, 
                    mensaje_texto: saludo, 
                    direccion: 'salida' 
                }]);
            }
        } catch (error) {
            console.error("❌ Error en Supabase:", error.message);
        }
    });

    console.log('🚀 Inicializando WhatsApp...');
    client.initialize();

}).catch(err => {
    console.error('❌ Error Mongo:', err.message);
    process.exit(1);
});