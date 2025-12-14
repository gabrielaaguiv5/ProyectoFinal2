require('dotenv').config(); 

// --- 1. NUEVAS IMPORTACIONES ---
const express = require('express');
const qrcodeLib = require('qrcode'); // Importar la librería 'qrcode' para generar la imagen
// ------------------------------

const { Client, RemoteAuth, MessageMedia } = require('whatsapp-web.js');
const { MongoStore } = require('wwebjs-mongo');
const mongoose = require('mongoose');
const qrcode = require('qrcode-terminal');
const { createClient } = require('@supabase/supabase-js');

// --- ⚠️ CONFIGURACIÓN CRÍTICA: USANDO VARIABLES DE ENTORNO ⚠️ ---
// ESTOS VALORES DEBEN ESTAR CONFIGURADOS EN EL DASHBOARD DE RAILWAY

// 1. CREDENCIALES DE SUPABASE
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;

// 2. CREDENCIALES DE MONGODB
const MONGO_URI = process.env.MONGO_URI;

// 3. Verificación de variables (CRÍTICO para despliegue)
if (!SUPABASE_URL || !SUPABASE_KEY || !MONGO_URI) {
    console.error('\n❌ ERROR DE CONFIGURACIÓN ❌');
    console.error('Faltan variables de entorno CRÍTICAS (SUPABASE_URL, SUPABASE_KEY, MONGO_URI).');
    console.error('Por favor, configúralas en el dashboard de Railway antes de desplegar.');
    process.exit(1);
}

// =========================================================
// === A. MANEJO DE ERRORES CRÍTICOS (AÑADIDO) ===
// =========================================================
process.on('uncaughtException', (err) => {
    console.error('\n🚨 ERROR CRÍTICO NO CAPTURADO (Uncaught Exception) 🚨');
    console.error('El proceso está a punto de salir. Causa:', err.message, err.stack);
    process.exit(1); 
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('\n⚠️ RECHAZO DE PROMESA NO MANEJADO (Unhandled Rejection) ⚠️');
    console.error('Razón:', reason);
});


// =========================================================
// === B. HEALTH CHECK DE EXPRESS (AÑADIDO) ===
// =========================================================
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.status(200).send('WhatsApp Bot process is alive and healthy.'); 
});

app.listen(port, () => {
    console.log(`[HEALTH CHECK] Express Server listening on port ${port}.`);
});
// =========================================================


// =========================================================
// === 1. DIAGNÓSTICO DE SUPABASE ===
// =========================================================
console.log('🔍 Validando credenciales de Supabase...');
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
const SUPABASE_BUCKET_NAME = 'qr-sessions'; // ⚠️ CAMBIA ESTO AL NOMBRE DE TU BUCKET DE SUPABASE STORAGE ⚠️

async function verificarConexionSupabase() {
    // ... (Tu función de verificación permanece igual) ...
    try {
        const { data, error } = await supabase.from('mensajes_whatsapp').select('*').limit(1);

        if (error) {
            console.error('\n❌ ERROR DE CONEXIÓN A SUPABASE (DB) ❌');
            console.error(`Mensaje: ${error.message}`);
            if (error.code === 'PGRST301' || error.message.includes('JWT')) {
                console.error('👉 CAUSA: Tu API KEY es incorrecta o no tiene permisos (revisa RLS).');
            } else if (error.code === 'ENOTFOUND') {
                console.error('👉 CAUSA: La URL de Supabase está mal escrita.');
            }
        } else {
            console.log('✅ SUPABASE (DB) FUNCIONANDO CORRECTAMENTE.');
        }
        
        // --- ADICIONAL: Verificar Supabase Storage ---
        // Esto verifica que el bucket exista.
        const { data: bucketData, error: bucketError } = await supabase.storage.getBucket(SUPABASE_BUCKET_NAME);
        if (bucketError || !bucketData) {
            console.error(`\n⚠️ ADVERTENCIA CRÍTICA: El bucket de Storage "${SUPABASE_BUCKET_NAME}" no existe o falló la conexión.`);
            console.error('👉 NECESITARÁS INICIALIZAR LOCALMENTE O CREAR EL BUCKET.');
        } else {
             console.log(`✅ SUPABASE (STORAGE: ${SUPABASE_BUCKET_NAME}) ACCESIBLE.`);
        }
    } catch (err) {
        console.error("Error crítico en Supabase:", err);
    }
}
verificarConexionSupabase();


// =========================================================
// === 2. CONEXIÓN A MONGODB Y ARRANQUE DEL BOT ===
// =========================================================
console.log('⏳ Iniciando conexión a MongoDB para RemoteAuth...');

mongoose.set('debug', false);

mongoose.connect(MONGO_URI)
    .then(() => {
        console.log('---------------------------------------------------');
        console.log('🎉 ¡CONEXIÓN A MONGODB EXITOSA! 🎉 (RemoteAuth Store)');
        console.log('---------------------------------------------------');
        
        const store = new MongoStore({ mongoose: mongoose });
        
        const client = new Client({
            authStrategy: new RemoteAuth({
                store: store,
                backupSyncIntervalMs: 60000, 
                dataPath: './'
            }),
            puppeteer: {
                headless: true,
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-extensions',
                    '--disable-gpu',
                    '--no-zygote',
                    '--no-first-run',
                    '--single-process',
                    '--disable-dev-shm-usage',
                    '--lang=en-US'
                ]
            }
        });
        
        // Función para obtener el texto o el tipo de mensaje para guardar
        const getMensajeTexto = (msg) => {
            if (msg.body && msg.body.length > 0) {
                return msg.body;
            }
            if (msg.type === 'chat') return null; 
            return `[${msg.type.toUpperCase()} COMPARTIDO]`;
        };

        // =========================================================
        // === NUEVA LÓGICA: GENERAR QR COMO IMAGEN EN SUPABASE (CRÍTICO) ===
        // =========================================================
        client.on('qr', async (qr) => {
            
            // 1. Mostrar QR corrupto en log (por si acaso)
            console.log('📱 ESCANEA ESTE QR (Intento de Terminal):');
            qrcode.generate(qr, { small: true });

            console.log('\n----------------------------------------------------');
            console.log('⏳ Generando imagen QR y subiendo a Supabase Storage...');

            try {
                // 2. Convertir el texto QR a un Buffer de imagen PNG
                const qrBuffer = await qrcodeLib.toBuffer(qr, { type: 'png' });
                
                // 3. Definir la ruta de almacenamiento con un timestamp
                const path = `temp-qr/session-${Date.now()}.png`;

                // 4. Subir el Buffer al bucket de Supabase
                const { error: uploadError } = await supabase.storage
                    .from(SUPABASE_BUCKET_NAME) 
                    .upload(path, qrBuffer, {
                        contentType: 'image/png',
                        upsert: true
                    });

                if (uploadError) {
                    console.error('❌ Error al subir QR a Supabase Storage:', uploadError.message);
                } else {
                    // 5. Obtener la URL pública para el escaneo
                    const { data: publicUrlData } = supabase.storage
                        .from(SUPABASE_BUCKET_NAME)
                        .getPublicUrl(path);

                    if (publicUrlData && publicUrlData.publicUrl) {
                        console.log('✅ QR DISPONIBLE EN URL ESCANEABLE (SOLO LA PRIMERA VEZ):');
                        console.log(`➡️ ${publicUrlData.publicUrl}`);
                        console.log('----------------------------------------------------');
                        console.log('ABRE ESTA URL EN TU NAVEGADOR Y ESCANEA LA IMAGEN.');
                    } else {
                         console.error('❌ No se pudo obtener la URL pública del QR.');
                    }
                }
            } catch (error) {
                 console.error('❌ Error fatal en la generación/subida del QR:', error);
            }
        });
        // =========================================================

        client.on('ready', () => {
            console.log('✅ BOT LISTO Y CONECTADO A WHATSAPP.');
        });

        client.on('remote_session_saved', () => {
            console.log('💾 Sesión guardada/actualizada en MongoDB. ¡La inestabilidad debería terminar aquí!');
        });
        
        client.on('disconnected', (reason) => {
            console.error('❌ Cliente desconectado. Razón:', reason);
        });


        client.on('message', async (msg) => {
            // ... (Tu lógica de mensajes y Supabase permanece igual) ...
            if (msg.from.includes('broadcast')) return; 
            if (msg.from.includes('@g.us')) return;      
            
            const mensajeGuardar = getMensajeTexto(msg);
            
            if (!mensajeGuardar) return; 

            const telefonoCliente = msg.from.replace('@c.us', '');

            try {
                let textoSalida = null;
                
                const { error: errorEntrada } = await supabase.from('mensajes_whatsapp').insert([{ 
                    telefono_origen: telefonoCliente, 
                    mensaje_texto: mensajeGuardar, 
                    direccion: 'entrada' 
                }]);
                if (errorEntrada) console.error("❌ Error guardando entrada en Supabase:", errorEntrada.message);

                
                if (msg.body.toLowerCase().includes('hola')) {
                    const respuestaDelBot = '¡Hola! Soy tu asistente virtual. ¿En qué te puedo servir hoy?';
                    await msg.reply(respuestaDelBot);
                    textoSalida = respuestaDelBot;
                    
                } else if (msg.body.toLowerCase().includes('foto') || msg.body.toLowerCase().includes('imagen')) {
                    await msg.reply("Simulación: Imagen de nuestro catálogo enviada.");
                    textoSalida = '[IMAGEN DE SALIDA ENVIADA]';
                }
                
                if (textoSalida) {
                    const { error: errorSalida } = await supabase.from('mensajes_whatsapp').insert([{ 
                        telefono_origen: telefonoCliente, 
                        mensaje_texto: textoSalida, 
                        direccion: 'salida' 
                    }]);
                    if (errorSalida) console.error("❌ Error guardando salida en Supabase:", errorSalida.message);
                }

            } catch (error) {
                console.error("❌ Error fatal en la lógica de Supabase:", error);
            }
        });

        console.log('🚀 Inicializando cliente de WhatsApp...');
        client.initialize();

    })
    .catch(err => {
        console.error('\n❌ ERROR CRÍTICO DE CONEXIÓN A MONGO ❌');
        console.error(`Razón: ${err.message}`);
        process.exit(1); 
    });