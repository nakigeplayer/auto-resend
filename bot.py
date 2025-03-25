import os
import traceback
from pyrogram import Client, filters
from pyrogram.types import Message

# Inicializa el cliente de Pyrogram con la sesión y las credenciales de API
app = Client("bot", 
             session_string=os.environ["SESSION_STRING"], 
             api_id=int(os.environ["API_ID"]), 
             api_hash=os.environ["API_HASH"])

# Variables de entorno adicionales
CHAT_ID = int(os.environ["CHAT_ID"])  # ID del chat a monitorear
KEYWORDS = os.environ["KEYWORDS"].split(",")  # Palabras clave separadas por comas
DESTINATIONS = os.environ["DESTINATIONS"].split(",")  # Lista de @usuarios o chat_ids
destination_index = 0  # Índice para controlar el destinatario

# Función para registrar todo (errores y acciones)
async def log_to_chat(client, log_message: str):
    try:
        await client.send_message(CHAT_ID, log_message)
    except Exception as e:
        print(f"No se pudo enviar el log al chat: {e}")

# Función para procesar y reenviar mensajes
@app.on_message(filters.chat(CHAT_ID) & filters.text & filters.media)
async def handle_message(client, message: Message):
    global destination_index

    try:
        # Registra que se recibió un mensaje
        await log_to_chat(client, f"Mensaje recibido:\n\n{message.text}")

        # Verifica si el texto contiene alguna de las palabras clave
        if any(keyword in message.text for keyword in KEYWORDS):
            # Obtén el destinatario actual
            destination = DESTINATIONS[destination_index]
            destination_index = (destination_index + 1) % len(DESTINATIONS)  # Rota al siguiente destinatario

            # Reenvía el mensaje
            forwarded_message = await message.forward(destination)

            # Registra la acción de reenvío
            await log_to_chat(client, f"Mensaje reenviado a: {destination}")

            # Responde al video reenviado con el mensaje "/convert"
            if forwarded_message.video:
                await forwarded_message.reply_text("/convert")
                await log_to_chat(client, f"Comando /convert enviado al mensaje reenviado en {destination}")

    except Exception as e:
        # Captura el error y registra el log detallado
        error_message = f"Se produjo un error:\n{traceback.format_exc()}"
        await log_to_chat(client, error_message)

if __name__ == "__main__":
    print("El bot está en funcionamiento...")
    app.run()
