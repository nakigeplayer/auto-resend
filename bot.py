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
CHAT_IDS = [int(chat_id) for chat_id in os.environ["CHAT_ID"].split(",")]  # IDs de los chats a monitorear
DESTINATIONS = os.environ["DESTINATIONS"].split(",")  # Lista de destinatarios
LOG_CHAT_ID = int(os.environ["LOG_CHAT_ID"])  # ID del chat para logs
CHANNEL_USERNAME = os.environ["CHANNEL_USERNAME"]  # @ del canal para videos
KEYWORDS = os.environ["KEYWORDS"].split(",")  # Palabras clave, separadas por comas
destination_index = 0  # Índice para rotar destinatarios


async def log_to_chat(client, log_message: str):
    """
    Enviar un mensaje al chat de logs para depuración.
    """
    try:
        await client.send_message(LOG_CHAT_ID, log_message)
    except Exception as e:
        print(f"No se pudo enviar el log: {e}")


@app.on_message(filters.chat(CHAT_IDS))
async def reenviar_a_destinatarios(client, message: Message):
    """
    Manejador para reenviar mensajes desde CHAT_IDS a DESTINATIONS sin incluir información del remitente original.
    """
    global destination_index

    try:
        # Obtener texto del mensaje o subtítulo (caption)
        texto_del_mensaje = message.text or message.caption or "Sin texto"

        # Registrar que se recibió un mensaje
        await log_to_chat(client, f"Mensaje recibido: {texto_del_mensaje}")

        # Verificar si el texto contiene alguna palabra clave
        if any(keyword.lower() in texto_del_mensaje.lower() for keyword in KEYWORDS):
            # Determinar el destinatario
            destination = DESTINATIONS[destination_index]
            destination_index = (destination_index + 1) % len(DESTINATIONS)

            # Recrear el mensaje sin información del remitente original
            if message.text:
                await client.send_message(destination, message.text)
            elif message.photo:
                await client.send_photo(destination, message.photo.file_id, caption=message.caption)
            elif message.video:
                await client.send_video(destination, message.video.file_id, caption=message.caption)
            elif message.document:
                await client.send_document(destination, message.document.file_id, caption=message.caption)

            # Log del reenvío
            await log_to_chat(client, f"Mensaje recreado y enviado a {destination}")

            # Enviar comando /convert si aplica
            if message.photo or message.video or message.document:
                await client.send_message(destination, "/convert")
                await log_to_chat(client, f"Comando /convert enviado en {destination}")

    except Exception as e:
        # Registrar errores
        error_message = f"Error procesando mensaje:\n{traceback.format_exc()}"
        await log_to_chat(client, error_message)
        print(error_message)


@app.on_message(filters.chat(DESTINATIONS) & filters.video)
async def reenviar_a_canal(client, message: Message):
    """
    Manejador para reenviar videos desde DESTINATIONS al canal sin información del remitente original.
    """
    try:
        # Recrear el video en el canal especificado
        await client.send_video(
            CHANNEL_USERNAME,
            message.video.file_id,
            caption=message.caption or "Sin subtítulo"
        )

        await log_to_chat(client, f"Video reenviado al canal {CHANNEL_USERNAME}")

    except Exception as e:
        # Registrar errores
        error_message = f"Error al reenviar video al canal:\n{traceback.format_exc()}"
        await log_to_chat(client, error_message)
        print(error_message)


if __name__ == "__main__":
    print("El bot está en funcionamiento...")
    app.run()
        
