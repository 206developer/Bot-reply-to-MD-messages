import discord
import requests

intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content

client = discord.Client(intents=intents)

# Webhook URL for the server
webhook_url = 'https://discord.com/api/webhooks/ID/TOKEN' 

# Dictionary to store user IDs and last received message
last_message_from_users = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Si el mensaje es un mensaje directo al bot
    if isinstance(message.channel, discord.DMChannel):
        user_id = message.author.id
        last_message_from_users[user_id] = message.content

        # Send the embed message to the webhook
        embed = discord.Embed(title="Nuevo mensaje", color=discord.Color.blue())
        embed.add_field(name="User:", value=f"{message.author.name} ({message.author.id})", inline=False)
        embed.add_field(name="Mensaje:", value=message.content, inline=False)
        requests.post(webhook_url, json={'embeds': [embed.to_dict()]})

    # Comando para responder al último mensaje recibido de un usuario
    if message.content.startswith('!responder'):
        params = message.content.split()
        if len(params) >= 3:
            try:
                user_id_to_reply = int(params[1])
            except ValueError:
                await message.channel.send('Please provide a valid user ID.')
                return  # Exit the function if the ID is invalid

            response = ' '.join(params[2:])

            if user_id_to_reply in last_message_from_users:
                # Use the user_id_to_reply directly
                user_to_reply = await client.fetch_user(user_id_to_reply) 
                # Check if the user was found
                if user_to_reply is not None:
                    # Send the response to the user's DM
                    await user_to_reply.send(f"Respuesta: {response}")
                else:
                    await message.channel.send('No se encontró un usuario con esa ID.')
            else:
                await message.channel.send('No se encontró un mensaje anterior de ese usuario.')

    # Comando para listar los chats abiertos
    if message.content.startswith('!rchats'):
        if last_message_from_users:
            response = "Chats abiertos:\n"
            for user_id, last_message in last_message_from_users.items():
                user = client.get_user(user_id)
                if user is not None:
                    response += f"- {user.name} ({user_id})\n"
            await message.channel.send(response)
        else:
            await message.channel.send("No hay chats abiertos.")

client.run('Token')  # Reemplaza 'TOKEN_DEL_BOT' con el token de tu propio bot
