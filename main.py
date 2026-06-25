import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# --- Environment Variables loaded from Render ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
TARGET_BOT = os.environ.get("TARGET_BOT", "@ChatBot") # Replace @ChatBot with the actual bot username in Render
STICKER_ID = os.environ.get("STICKER_ID", "") 

# Initialize the Telegram Client
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=TARGET_BOT))
async def handler(event):
    text = event.raw_text
    
    # 1. When the bot connects you to a partner
    if 'Start chatting!' in text or 'Partner found' in text:
        print("Partner found. Sending sticker...")
        await asyncio.sleep(1) # Tiny delay to look natural and avoid bans
        
        # Send the sticker using its File ID
        try:
            if STICKER_ID:
                await client.send_file(event.chat_id, STICKER_ID)
            else:
                print("Error: STICKER_ID environment variable is missing!")
        except Exception as e:
            print(f"Could not send sticker: {e}")
        
        await asyncio.sleep(1) # Tiny delay before skipping
        print("Skipping partner...")
        await event.respond('/stop')
        
    # 2. When you leave the chat, or search is taking too long
    elif 'You left the chat' in text or 'search is taking too long' in text.lower():
        print("Searching for new partner...")
        await asyncio.sleep(1)
        await event.respond('⚡️ Find a Partner') # Replace with the exact button text if different

# --- Dummy web server to keep Render Web Service active ---
async def handle(request):
    return web.Response(text="Telegram Userbot is running successfully!")

async def main():
    # Start the Telegram client
    await client.start()
    print("Userbot successfully connected to Telegram!")
    
    # Start the web server
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")
    
    # Keep the client running indefinitely
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())

