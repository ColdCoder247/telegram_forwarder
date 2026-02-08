import asyncio
import os
import random
from telethon import TelegramClient, errors
from hashlib import md5
from datetime import datetime

# === CONFIG ===
api_id = 25207645
api_hash = '0a1e4359661414bd09455120935ebecd'
source_group = '-1003015134054'  # Use @username or group ID
destination_groups = ['@JK_HDSGIJ_HPUHSA_mfdgsdgjkhiuahs']

# Added channel variable
channel = "Moonknight Drama"

# Safe delay between messages
min_delay = 8
max_delay = 15

# Pause every N messages
pause_every = 35
pause_time = 300  # seconds (5 minutes)

# File paths
hashes_file = 'forwarded_hashes.txt'
log_file = 'forward_log.txt'
duplicates_file = 'duplicates_log.txt'
resume_file = 'last_message_id.txt'
forwarded_hashes = set()

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
    return None

def save_last_id(message_id):
    with open(resume_file, 'w') as f:
        f.write(str(message_id))

client = TelegramClient('forward_session', api_id, api_hash)

async def forward_history():
    load_hashes()
    await client.start()
    print("✅ Bot started: Fetching full history...")

    # ✅ FIXED: Corrected source group resolution using get_input_entity
    try:
        if source_group.startswith("-100"):
            source_entity = await client.get_input_entity(int(source_group))
        else:
            source_entity = await client.get_entity(source_group)
        print(f"📌 Reading messages from: {getattr(source_entity, 'title', str(source_entity))}")
    except Exception as e:
        print(f"❌ Failed to resolve source: {e}")
        return

    # Resolve destination group(s)
    resolved_destinations = []
    for dest in destination_groups:
        try:
            entity = await client.get_entity(dest)
            resolved_destinations.append(entity)
            print(f"✅ Destination ready: {getattr(entity, 'title', str(entity.id))}")
        except Exception as e:
            print(f"❌ Failed to resolve destination '{dest}': {e}")

    if not resolved_destinations:
        print("❌ No valid destinations. Exiting.")
        return

    # ✅ Send "Started" message before forwarding
    for dest in resolved_destinations:
        try:
            await client.send_message(dest, f"======= Started {channel}")
        except Exception as e:
            print(f"❌ Failed to send start message to {dest.id}: {e}")

    forwarded_count = 0
    last_forwarded_id = load_last_id()

    async for message in client.iter_messages(source_entity, reverse=True, offset_id=last_forwarded_id or 0):
        if is_sticker(message):
            log(duplicates_file, "Skipped sticker message")
            continue

        msg_hash = hash_message(message)
        if not msg_hash:
            continue

        if msg_hash in forwarded_hashes:
            log(duplicates_file, f"Skipped duplicate: {message.text or 'Media'}")
            continue

        for dest in resolved_destinations:
            try:
                await asyncio.sleep(random.uniform(min_delay, max_delay))

                if message.media:
                    # ✅ Preserve thumbnail only if already embedded (no extra download)
                    if hasattr(message.media, 'document') and getattr(message.media.document, 'thumbs', None):
                        thumb = message.media.document.thumbs[0] if message.media.document.thumbs else None
                        if thumb:
                            await client.send_file(dest, message.media, caption=message.text or '', thumb=thumb)
                        else:
                            await client.send_file(dest, message.media, caption=message.text or '')
                    else:
                        await client.send_file(dest, message.media, caption=message.text or '')
                else:
                    await client.send_message(dest, message.text)

                log(log_file, f"Forwarded to {dest.id}: {message.text or 'Media'}")
                print(f"✅ Forwarded message: {message.text or 'Media'}")
                forwarded_count += 1
                save_last_id(message.id)

            except errors.FloodWaitError as e:
                print(f"⏳ Flood wait: sleeping {e.seconds} seconds")
                await asyncio.sleep(e.seconds + 5)
            except Exception as e:
                print(f"❌ Error forwarding to {dest.id}: {e}")
                log(log_file, f"Failed to forward to {dest.id}: {e}")

        forwarded_hashes.add(msg_hash)
        save_hash(msg_hash)

        # ⏸ Auto-pause after N messages
        if forwarded_count % pause_every == 0:
            print(f"⏸ Pausing for {pause_time // 60} minutes to avoid flood detection...")
            await asyncio.sleep(pause_time)

    # ✅ Send the "Till Now Done" message
    for dest in resolved_destinations:
        try:
            await client.send_message(dest, f"Till Now Done {channel}")
        except Exception as e:
            print(f"❌ Failed to send completion message to {dest.id}: {e}")

    print(f"🎉 Done forwarding {forwarded_count} message(s).")

try:
    client.loop.run_until_complete(forward_history())
except KeyboardInterrupt:
    print("\n🛑 Bot stopped by user.")
