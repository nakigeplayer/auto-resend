import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Inicializa el cliente de Pyrogram con la session string de las variables de entorno
app = Client("bot", session_string=os.environ["SESSION_STRING"])

# Variables de entorno para la configuración
CHAT_ID = int(os.environ["CHAT_ID"])  # ID del chat a monitorear
KEYWORDS = os.environ["KEYWORDS"].split(",")  # Palabras clave separadas por comas
DESTINATIONS = os.environ["DESTINATIONS"].split(",")  # Lista de @usuarios o chat_ids
destination_index = 0  # Índice para controlar el destinatario

# Función para procesar y reenviar mensajes
@app.on_message(filters.chat(CHAT_ID) & filters.text & filters.media)
async def handle_message(client, message: Message):
    global destination_index

    # Verifica si el texto contiene alguna de las palabras clave
    if any(keyword in message.text for keyword in KEYWORDS):
        # Obtén el destinatario actual
        destination = DESTINATIONS[destination_index]
        destination_index = (destination_index + 1) % len(DESTINATIONS)  # Rota al siguiente destinatario

        # Reenvía el mensaje
        forwarded_message = await message.forward(destination)

        # Responde al video reenviado con el mensaje "/convert"
        if forwarded_message.video:
            await forwarded_message.reply_text("/convert")

if __name__ == "__main__":
    print("El bot está en funcionamiento...")
    app.run()
