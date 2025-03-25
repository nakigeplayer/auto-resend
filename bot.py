import os
import traceback
from pyrogram import Client, filters
from pyrogram.types import Message

# Inicializar Pyrogram con la sesión y credenciales
app = Client(
    "bot",
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"],
    session_string=os.environ["SESSION_STRING"]
)

# Variables de entorno necesarias
CHAT_ID = int(os.environ["CHAT_ID"])  # ID del chat a monitorear
KEYWORDS = os.environ["KEYWORDS"].split(",")  # Palabras clave, separadas por comas
DESTINATIONS = os.environ["DESTINATIONS"].split(",")  # Lista de destinatarios
LOG_CHAT_ID = int(os.environ["LOG_CHAT_ID"])  # ID del chat para logs
destination_index = 0  # Índice para rotar destinatarios


async def log_to_chat(client, log_message: str):
    """
    Enviar un mensaje al chat de logs para depuración.
    """
    try:
        await client.send_message(LOG_CHAT_ID, log_message)
    except Exception as e:
        print(f"No se pudo enviar el log: {e}")


@app.on_message(filters.chat(CHAT_ID) & filters.text)
async def handle_message(client, message: Message):
    """
    Procesar mensajes de un chat específico.
    """
    global destination_index

    try:
        # Registrar que se recibió un mensaje
        await log_to_chat(client, f"Mensaje recibido: {message.text}")

        # Verificar palabras clave
        if any(keyword in message.text.lower() for keyword in KEYWORDS):
            # Determinar el destinatario
            destination = DESTINATIONS[destination_index]
            destination_index = (destination_index + 1) % len(DESTINATIONS)

            # Reenviar el mensaje
            forwarded_message = await message.forward(destination)

            # Log de reenvío
            await log_to_chat(client, f"Mensaje reenviado a {destination}: {forwarded_message.link}")

            # Enviar "/convert" si es un video
            if message.video:
                await forwarded_message.reply_text("/convert")
                await log_to_chat(client, f"Comando /convert enviado en {destination}")

    except Exception as e:
        # Registrar errores
        error_message = f"Error procesando mensaje:\n{traceback.format_exc()}"
        await log_to_chat(client, error_message)
        print(error_message)

print("El bot está en funcionamiento...")
app.run()
print("El bot está en funcionamiento...")
