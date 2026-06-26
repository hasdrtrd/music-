import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# --- Environment Variables loaded from Render ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
TARGET_BOT = os.environ.get("TARGET_BOT", "@username_of_the_bot") 

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

async def get_fresh_sticker():
    """Helper function to fetch the latest sticker dynamically right when needed"""
    try:
        async for message in client.iter_messages('me', limit=20):
            if message.sticker:
                return message.document
    except Exception as e:
        print(f"Error fetching fresh sticker: {e}")
    return None

@client.on(events.NewMessage(chats=TARGET_BOT))
async def handler(event):
    text = event.raw_text
    
    # 1. When the bot connects you to a partner
    if 'Start chatting!' in text:
        print("Partner found. Fetching live sticker from Saved Messages...")
        await asyncio.sleep(1) 
        
        # FIXED: Grabbing a completely fresh token so it never expires
        current_sticker = await get_fresh_sticker()
        
        try:
            if current_sticker:
                await client.send_file(event.chat_id, current_sticker)
                print("Sticker sent successfully!")
            else:
                await event.respond('❌ ERROR: I could not find a sticker in your Saved Messages!')
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
    return web.Response(text="Telegram Userbot is running and checking Saved Messages!")

async def main():
    await client.start()
    print("Userbot successfully connected to Telegram!")
    
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
    
