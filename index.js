require('dotenv').config();
const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const { createClient } = require('@supabase/supabase-js');
const qrcodeLib = require('qrcode');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

app.get('/', (req, res) => res.send('Bot Activo'));
app.listen(port, '0.0.0.0', () => console.log(`🚀 Puerto ${port} abierto`));

// CONFIGURACIÓN PARA USAR EL VOLUMEN
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: 'session',
        dataPath: path.join(__dirname, '.wwebjs_auth') // Carpeta en el Volumen
    }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// GENERADOR DE LINK (Sin condiciones, siempre se ejecuta)
client.on('qr', async (qr) => {
    console.log('📱 QR RECIBIDO. SUBIENDO A SUPABASE...');
    try {
        const qrBuffer = await qrcodeLib.toBuffer(qr, { type: 'png' });
        const fileName = `temp-qr/${Date.now()}.png`;
        
        await supabase.storage.from('qr-sessions').upload(fileName, qrBuffer, {
            contentType: 'image/png', 
            upsert: true
        });

        const { data } = supabase.storage.from('qr-sessions').getPublicUrl(fileName);
        
        console.log('\n**************************************');
        console.log(`➡️ ESCANEA AQUÍ: ${data.publicUrl}`);
        console.log('**************************************\n');
    } catch (e) {
        console.error('❌ Error Supabase:', e.message);
    }
});

client.on('ready', () => console.log('✅ CONECTADO Y GUARDADO EN VOLUMEN'));

console.log('⏳ Iniciando Cliente...');
client.initialize();