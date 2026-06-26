import os
import asyncio
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# --- Environment Variables ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
TARGET_BOTS = [bot.strip() for bot in os.environ.get("TARGET_BOT", "@username").split(",")]

# List of messages to rotate through
PROMO_MESSAGES = [
    "tbh there's better bot than this, search instanttalk bot and enjoy",
    "tired of this bot? search instanttalk bot for a better experience",
    "this bot is mid, try instanttalk bot instead",
    "looking for better features? try searching instanttalk bot",
    "stop using this, search instanttalk bot and thank me later"
]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

bot2_next_limit_reached = False

async def get_stickers():
    stickers = []
    try:
        async for message in client.iter_messages('me', limit=40):
            if message.sticker:
                stickers.append(message.document)
            if len(stickers) >= 3: break
    except Exception as e:
        print(f"Error: {e}")
    return stickers

@client.on(events.NewMessage(chats=TARGET_BOTS))
async def handler(event):
    global bot2_next_limit_reached
    text = event.raw_text
    stickers = await get_stickers()
    msg = random.choice(PROMO_MESSAGES) # Pick a random message

    # ==========================================
    # BOT 1
    # ==========================================
    if 'Start chatting!' in text:
        await asyncio.sleep(1)
        try: await event.respond(msg)
        except: pass
        await asyncio.sleep(0.5)
        if len(stickers) >= 1: await client.send_file(event.chat_id, stickers[0])
        await asyncio.sleep(1.5)
        await event.respond('/stop')
        
    elif any(phrase in text for phrase in ['You left the chat', 'I\'m an anonymous chat bot', 'Your partner ended the chat', 'Rate your partner']):
        await asyncio.sleep(1)
        await event.respond('/search')

    # ==========================================
    # BOT 2
    # ==========================================
    elif 'Partner found 😺' in text:
        await asyncio.sleep(1)
        try: await event.respond(msg)
        except: pass
        await asyncio.sleep(0.5)
        if len(stickers) >= 2: await client.send_file(event.chat_id, stickers[1])
        elif len(stickers) >= 1: await client.send_file(event.chat_id, stickers[0])
        
        await asyncio.sleep(2)
        if bot2_next_limit_reached: await event.respond('/stop')
        else: await event.respond('/next')

    elif "daily /next limit" in text:
        bot2_next_limit_reached = True
        await asyncio.sleep(1)
        await event.respond('/stop')

    # ==========================================
    # BOT 3: "Anonymous Chat - Dating, Random"
    # ==========================================
    elif 'Found someone!' in text:
        print("Bot 3: Partner found.")
        await asyncio.sleep(1.5)
        
        # Send text message
        try: 
            await event.respond(msg)
        except: 
            pass
        
        await asyncio.sleep(1)
        
        # Try sending sticker, but catch the "I can't send these" error so it doesn't crash
        try:
            stickers = await get_stickers()
            if len(stickers) >= 3: 
                await client.send_file(event.chat_id, stickers[2])
            elif len(stickers) >= 1: 
                await client.send_file(event.chat_id, stickers[0])
        except Exception as e:
            print(f"Bot 3 blocked the sticker: {e}")
            
        await asyncio.sleep(1)
        await event.respond('/next')

    # Catch-all to restart loop if bot gets stuck
    elif 'Room:' in text or 'Reactions:' in text:
        # If the bot is stuck in a room but no action was taken, force skip
        await asyncio.sleep(2)
        await event.respond('/next')
        

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
