import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
TARGET_BOTS = [bot.strip() for bot in os.environ.get("TARGET_BOT", "@username").split(",")]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

bot2_next_limit_reached = False

async def get_stickers():
    stickers = []
    try:
        async for message in client.iter_messages('me', limit=30):
            if message.sticker:
                stickers.append(message.document)
            if len(stickers) >= 2: break
    except Exception as e:
        print(f"Error: {e}")
    return stickers

@client.on(events.NewMessage(chats=TARGET_BOTS))
async def handler(event):
    global bot2_next_limit_reached
    text = event.raw_text
    
    # ==========================================
    # BOT 2: "𝐌𝐮𝐭𝐮𝐚𝐥 ⋆ Anonymous Chat" Logic
    # ==========================================
    # Only act if it's a real chat, not a search status or menu
    if 'Partner found 😺' in text:
        print("Bot 2: Partner found.")
        await asyncio.sleep(1) 
        
        stickers = await get_stickers()
        # Use sticker index 1 for Bot 2
        if len(stickers) >= 2:
            await client.send_file(event.chat_id, stickers[1])
        elif len(stickers) >= 1:
            await client.send_file(event.chat_id, stickers[0])
        
        await asyncio.sleep(2) 
        if bot2_next_limit_reached:
            await event.respond('/stop')
        else:
            await event.respond('/next') 

    # ONLY trigger search if the bot confirms the chat is truly over
    elif any(phrase in text for phrase in [
        'You stopped the chat', 
        'Your partner has stopped the chat', 
        'Type /search to find a new partner'
    ]):
        print("Bot 2: Chat ended properly. Searching...")
        await asyncio.sleep(1)
        await event.respond('/search')

    # Catch limit
    elif "daily /next limit" in text:
        bot2_next_limit_reached = True
        await asyncio.sleep(1)
        await event.respond('/stop')

# --- Dummy web server ---
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

