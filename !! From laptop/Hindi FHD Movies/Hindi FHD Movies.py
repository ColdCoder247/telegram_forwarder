import asyncio
import os
import random
from telethon import TelegramClient, errors
from hashlib import md5
from datetime import datetime

# === CONFIG ===
api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")
source_group = '-1002394425543'  # Use @username or group ID
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

# ---------- Helpers ----------

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

def is_sticker(message):
    if message.sticker:
        return True
    if message.document and message.document.mime_type in ['image/webp', 'application/x-tgsticker']:
        return True
    return False

def load_last_id():
    if os.path.exists(resume_file):
        with open(resume_file, 'r') as f:
            return int(f.read().strip())
    return 0

def save_last_id(message_id):
    with open(resume_file, 'w') as f:
        f.write(str(message_id))

# ---------- Client ----------

client = TelegramClient('forward_session', api_id, api_hash)

async def forward_history():
    load_hashes()
    await client.start()
    print("✅ Bot started: Fetching full history...")

    # Resolve source
    try:
        if source_group.startswith("-100"):
            source_entity = await client.get_input_entity(int(source_group))
        else:
            source_entity = await client.get_entity(source_group)
    except Exception as e:
        print(f"❌ Failed to resolve source: {e}")
        return

    # Resolve destinations
    resolved_destinations = []
    for dest in destination_groups:
        try:
            resolved_destinations.append(await client.get_entity(dest))
        except Exception as e:
            print(f"❌ Failed to resolve destination {dest}: {e}")

    if not resolved_destinations:
        print("❌ No valid destinations.")
        return

    for dest in resolved_destinations:
        await client.send_message(dest, f"======= Started {channel}")

    forwarded_count = 0
    last_id = load_last_id()

    async for message in client.iter_messages(
        source_entity,
        reverse=True,
        offset_id=last_id
    ):
        try:
            # ALWAYS update ID at end of loop
            current_id = message.id

            if is_sticker(message):
                log(duplicates_file, "Skipped sticker")
                continue

            msg_hash = hash_message(message)
            if not msg_hash:
                continue

            if msg_hash in forwarded_hashes:
                log(duplicates_file, f"Skipped duplicate: {current_id}")
                continue

            for dest in resolved_destinations:
                try:
                    await asyncio.sleep(random.uniform(min_delay, max_delay))

                    if message.media:
                        await client.send_file(dest, message.media, caption=message.text or '')
                    else:
                        await client.send_message(dest, message.text)

                except errors.FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 5)
                except Exception as e:
                    log(log_file, f"Failed {current_id}: {e}")

            forwarded_hashes.add(msg_hash)
            save_hash(msg_hash)
            forwarded_count += 1

        finally:
            # ✅ CRITICAL FIX: always save last processed ID
            save_last_id(message.id)

            if forwarded_count and forwarded_count % pause_every == 0:
                print(f"⏸ Pausing {pause_time//60} minutes...")
                await asyncio.sleep(pause_time)

    for dest in resolved_destinations:
        await client.send_message(dest, f"Till Now Done {channel}")

    print(f"🎉 Done forwarding {forwarded_count} messages.")

try:
    client.loop.run_until_complete(forward_history())
except KeyboardInterrupt:
    print("🛑 Bot stopped.")
