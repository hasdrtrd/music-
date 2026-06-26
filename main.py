import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# --- Environment Variables loaded from Render ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# Support multiple bots: Split by comma
TARGET_BOTS = [bot.strip() for bot in os.environ.get("TARGET_BOT", "@username_of_the_bot").split(",")]

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

@client.on(events.NewMessage(chats=TARGET_BOTS))
async def handler(event):
    text = event.raw_text
    
    # ==========================================
    # BOT 1: "Dating💜 - Anonymous Chat" Logic
    # ==========================================
    if 'Start chatting!' in text:
        print("Bot 1: Partner found. Sending sticker...")
        await asyncio.sleep(1) 
        
        current_sticker = await get_fresh_sticker()
        try:
            if current_sticker:
                await client.send_file(event.chat_id, current_sticker)
        except Exception as e:
            print(f'❌ ERROR: {e}')
        
        await asyncio.sleep(1.5) 
        print("Bot 1: Skipping partner...")
        await event.respond('/stop')
        
    elif any(phrase in text for phrase in [
        'You left the chat', 
        "I'm an anonymous chat bot", 
        'Your partner ended the chat', 
        'Rate your partner'
    ]):
        print("Bot 1: Chat ended. Searching for new partner...")
        await asyncio.sleep(1)
        await event.respond('/search') 

    # ==========================================
    # BOT 2: "𝐌𝐮𝐭𝐮𝐚𝐥 ⋆ Anonymous Chat" Logic
    # ==========================================
    elif 'Partner found 😺' in text:
        print("Bot 2: Partner found. Sending sticker...")
        await asyncio.sleep(1) 
        
        current_sticker = await get_fresh_sticker()
        try:
            if current_sticker:
                await client.send_file(event.chat_id, current_sticker)
        except Exception as e:
            print(f'❌ ERROR: {e}')
        
        # INCREASED DELAY to 2 seconds to avoid the "Wait 1s" spam filter
        await asyncio.sleep(2) 
        print("Bot 2: Skipping partner...")
        await event.respond('/next') 

    # Catch when the partner skips you first
    elif 'Your partner has stopped the chat 😞' in text:
        print("Bot 2: Partner left. Searching for new partner...")
        await asyncio.sleep(1)
        await event.respond('/search')
        
    # Catch the cooldown warning just in case it ever happens again
    elif 'Wait' in text and '/next' in text:
        print("Bot 2: Cooldown hit. Waiting and retrying...")
        await asyncio.sleep(2)
        await event.respond('/next')

# --- Dummy web server to keep Render Web Service active ---
async def handle(request):
    return web.Response(text=f"Telegram Userbot is running and listening to: {', '.join(TARGET_BOTS)}")

async def main():
    await client.start()
    print(f"Userbot successfully connected! Listening to bots: {TARGET_BOTS}")
    
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
        
