import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# --- Environment Variables ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
TARGET_BOTS = [bot.strip() for bot in os.environ.get("TARGET_BOT", "@username").split(",")]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Tracks limit for Bot 2
bot2_next_limit_reached = False

async def get_stickers():
    """Fetches the two most recent stickers from Saved Messages"""
    stickers = []
    try:
        async for message in client.iter_messages('me', limit=30):
            if message.sticker:
                stickers.append(message.document)
            if len(stickers) >= 2:
                break
    except Exception as e:
        print(f"Error fetching stickers: {e}")
    return stickers

@client.on(events.NewMessage(chats=TARGET_BOTS))
async def handler(event):
    global bot2_next_limit_reached
    text = event.raw_text
    chat_username = (await event.get_chat()).username
    
    # Refresh sticker list
    stickers = await get_stickers()
    
    # ==========================================
    # BOT 1 Logic
    # ==========================================
    if 'Start chatting!' in text:
        print("Bot 1: Partner found.")
        await asyncio.sleep(1) 
        
        # Use the first sticker for Bot 1
        if len(stickers) >= 1:
            await client.send_file(event.chat_id, stickers[0])
        
        await asyncio.sleep(1.5) 
        await event.respond('/stop')
        
    elif any(phrase in text for phrase in ['You left the chat', "I'm an anonymous chat bot", 'Your partner ended the chat', 'Rate your partner']):
        await asyncio.sleep(1)
        await event.respond('/search') 

    # ==========================================
    # BOT 2 Logic
    # ==========================================
    elif 'Partner found 😺' in text:
        print("Bot 2: Partner found.")
        await asyncio.sleep(1) 
        
        # Use the second sticker for Bot 2
        if len(stickers) >= 2:
            await client.send_file(event.chat_id, stickers[1])
        elif len(stickers) >= 1:
            await client.send_file(event.chat_id, stickers[0]) # Fallback to first if only one exists
        
        await asyncio.sleep(2) 
        if bot2_next_limit_reached:
            await event.respond('/stop')
        else:
            await event.respond('/next') 

    elif "You've reached the daily /next limit" in text:
        bot2_next_limit_reached = True
        await event.respond('/stop')

    elif any(phrase in text for phrase in ['Your partner has stopped the chat', 'You stopped the chat']):
        await event.respond('/search')

# --- Server Keep-Alive ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    await client.start()
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080))).start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
        
