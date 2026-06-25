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

# Global variable to hold the actual sticker
my_sticker = None

@client.on(events.NewMessage(chats=TARGET_BOT))
async def handler(event):
    text = event.raw_text
    
    # 1. When the bot connects you to a partner
    if 'Start chatting!' in text:
        print("Partner found. Sending sticker...")
        await asyncio.sleep(1) 
        
        # Send the sticker we grabbed from Saved Messages
        try:
            if my_sticker:
                await client.send_file(event.chat_id, my_sticker)
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
    global my_sticker
    await client.start()
    print("Userbot successfully connected to Telegram!")
    
    # Check "Saved Messages" for the sticker on startup
    print("Looking for a sticker in your Saved Messages...")
    try:
        # iter_messages('me') looks at your Saved Messages
        async for message in client.iter_messages('me', limit=20):
            if message.sticker:
                my_sticker = message.document
                print("✅ Successfully loaded sticker from Saved Messages!")
                break
                
        if not my_sticker:
            print("⚠️ Could not find any sticker in the last 20 messages of your Saved Messages.")
    except Exception as e:
        print(f"Error checking Saved Messages: {e}")
    
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
                
