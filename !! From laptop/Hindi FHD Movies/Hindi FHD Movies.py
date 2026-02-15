import asyncio
import os
import random
from telethon import TelegramClient, errors
from hashlib import md5
from datetime import datetime

# === CONFIG ===
api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")

source_group = '-1002394425543'
destination_groups = ['@JK_HDSGIJ_HPUHSA_mfdgsdgjkhiuahs']

channel = "Hindi FHD Movies"

min_delay = 8
max_delay = 15

pause_every = 35
pause_time = 300  # seconds

hashes_file = 'forwarded_hashes.txt'
log_file = 'forward_log.txt'
duplicates_file = 'duplicates_log.txt'
resume_file = 'last_message_id.txt'

forwarded_hashes = set()

client = TelegramClient('forward_session', api_id, api_hash)

# ================= HELPERS =================

def load_hashes():
    if os.path.exists(hashes_file):
        with open(hashes_file, 'r', encoding='utf-8') as f:
            for line in f:
                forwarded_hashes.add(line.strip())

def save_hash(msg_hash):
    with open(hashes_file, 'a', encoding='utf-8') as f:
        f.write(msg_hash + '\n')

def log(file, msg):
    with open(file, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def hash_message(message):
    if message.text:
        return md5(message.text.encode('utf-8')).hexdigest()
    elif message.media:
        return f"{message.media.__class__.__name__}_{message.id}"
    return None

def load_last_id():
    if os.path.exists(resume_file):
        with open(resume_file, 'r') as f:
            return int(f.read().strip())
    return 0

def save_last_id(message_id):
    with open(resume_file, 'w') as f:
        f.write(str(message_id))

# ================= MAIN =================

async def forward_history():
    load_hashes()
    await client.start()
    print("✅ Bot started")

    # Resolve source
    if source_group.startswith("-100"):
        source_entity = await client.get_input_entity(int(source_group))
    else:
        source_entity = await client.get_entity(source_group)

    # Resolve destinations
    resolved_destinations = []
    for dest in destination_groups:
        entity = await client.get_entity(dest)
        resolved_destinations.append(entity)

    # Send start message
    for dest in resolved_destinations:
        await client.send_message(dest, f"======= Started {channel}")

    last_forwarded_id = load_last_id()
    forwarded_count = 0

    async for message in client.iter_messages(
            source_entity,
            min_id=last_forwarded_id,
            reverse=True
    ):

        msg_hash = hash_message(message)
        if not msg_hash:
            continue

        if msg_hash in forwarded_hashes:
            log(duplicates_file, "Skipped duplicate")
            continue

        # 🔥 Only forward VIDEO files (skip images/logos/stickers)
        if not (message.document and 
                message.document.mime_type and 
                message.document.mime_type.startswith("video")):
            continue

        for dest in resolved_destinations:
            try:
                await asyncio.sleep(random.uniform(min_delay, max_delay))

                # Preserve thumbnail if exists
                if getattr(message.document, 'thumbs', None):
                    thumb = message.document.thumbs[0] if message.document.thumbs else None
                    if thumb:
                        await client.send_file(dest, message.document, caption=message.text or '', thumb=thumb)
                    else:
                        await client.send_file(dest, message.document, caption=message.text or '')
                else:
                    await client.send_file(dest, message.document, caption=message.text or '')

                log(log_file, f"Sent video to {dest.id}")
                print(f"✅ Sent video: {message.id}")

                save_last_id(message.id)
                forwarded_count += 1

            except errors.FloodWaitError as e:
                print(f"⏳ Flood wait: sleeping {e.seconds} seconds")
                await asyncio.sleep(e.seconds + 5)

            except Exception as e:
                print(f"❌ Error forwarding to {dest.id}: {e}")
                log(log_file, f"Failed to forward to {dest.id}: {e}")

        forwarded_hashes.add(msg_hash)
        save_hash(msg_hash)

        if forwarded_count % pause_every == 0:
            print(f"⏸ Pausing for {pause_time // 60} minutes...")
            await asyncio.sleep(pause_time)

    # Send completion message
    for dest in resolved_destinations:
        await client.send_message(dest, f"Till Now Done {channel}")

    print(f"🎉 Done forwarding {forwarded_count} message(s).")

# ================= RUN =================

try:
    client.loop.run_until_complete(forward_history())
except KeyboardInterrupt:
    print("\n🛑 Bot stopped by user.")
