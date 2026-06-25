import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName
from aiohttp import web

# --- Environment Variables loaded from Render ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
TARGET_BOT = os.environ.get("TARGET_BOT", "@username_of_the_bot") 

# Using the exact set_name from your previous message
STICKER_SET_NAME = os.environ.get("STICKER_SET_NAME", "pk_6204240_by_Ctikerubot")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Global variable to store the actual sticker object once loaded
my_sticker = None

@client.on(events.NewMessage(chats=TARGET_BOT))
async def handler(event):
    text = event.raw_text
    
    # 1. When the bot connects you to a partner
    if 'Start chatting!' in text:
        print("Partner found. Sending sticker directly from set...")
        await asyncio.sleep(1) 
        
        # Send the sticker object we loaded from the set
        try:
            if my_sticker:
                await client.send_file(event.chat_id, my_sticker)
            else:
                await event.respond('❌ ERROR: Sticker was not loaded from the set properly.')
        except Exception as e:
            await event.respond(f'❌ ERROR SENDING STICKER: {e}')
        
        await asyncio.sleep(1) 
        print("Skipping partner...")
        await event.respond('/stop')
        
    # 2. When you leave the chat or hit the main menu
    elif 'You left the chat' in text or "I'm an anonymous chat bot" in text:
        print("Searching for new partner...")
        await asyncio.sleep(1)
        await event.respond('/search') 

# --- Dummy web server to keep Render Web Service active ---
async def handle(request):
    return web.Response(text="Telegram Userbot is running with a live Sticker Set!")

async def main():
    global my_sticker
    await client.start()
    print("Userbot successfully connected to Telegram!")
    
    # Load the sticker set directly from Telegram's servers on startup
    try:
        print(f"Fetching sticker set: {STICKER_SET_NAME}...")
        sticker_set = await client(GetStickerSetRequest(
            stickerset=InputStickerSetShortName(short_name=STICKER_SET_NAME)
        ))
        
        # Grab the first sticker in the pack (Index 0)
        my_sticker = sticker_set.documents[0] 
        print("Successfully grabbed sticker from the set!")
    except Exception as e:
        print(f"Failed to load sticker set: {e}")
    
    # Start web server
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
