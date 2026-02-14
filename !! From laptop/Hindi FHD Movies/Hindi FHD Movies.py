import asyncio
import os
import random
import subprocess
from telethon import TelegramClient, errors
from hashlib import md5
from datetime import datetime

# ================= CONFIG =================

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")

if not api_id or not api_hash:
    raise ValueError("❌ Missing Telegram API credentials.")

source_group = '-1002394425543'
destination_groups = ['@JK_HDSGIJ_HPUHSA_mfdgsdgjkhiuahs']

channel = "Hindi FHD Movies"

min_delay = 8
max_delay = 15

pause_every = 35
pause_time = 300

checkpoint_every = 5  # 🔥 checkpoint every 20 messages

hashes_file = 'forwarded_hashes.txt'
resume_file = 'last_message_id.txt'

forwarded_hashes = set()

# ================= UTILITIES =================

def git_checkpoint():
    try:
        subprocess.run(["git", "add", "."], check=True)
        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Auto-checkpoint"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("💾 Mid-run checkpoint committed")
    except Exception as e:
        print(f"⚠️ Checkpoint failed: {e}")

def load_hashes():
    if os.path.exists(hashes_file):
        with open(hashes_file, 'r', encoding='utf-8') as f:
            forwarded_hashes.update(line.strip() for line in f)

def save_hash(msg_hash):
    with open(hashes_file, 'a', encoding='utf-8') as f:
        f.write(msg_hash + '\n')

def load_last_id():
    if os.path.exists(resume_file):
        with open(resume_file, 'r') as f:
            return int(f.read().strip())
    return 0

def save_last_id(message_id):
    with open(resume_file, 'w') as f:
        f.write(str(message_id))

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

# ================= CLIENT =================

client = TelegramClient('forward_session', api_id, api_hash)

async def forward_history():
    load_hashes()
    await client.start()

    source_entity = await client.get_entity(int(source_group)) \
        if source_group.startswith("-100") else await client.get_entity(source_group)

    resolved_destinations = [
        await client.get_entity(dest) for dest in destination_groups
    ]

    forwarded_count = 0
    last_forwarded_id = load_last_id()

    async for message in client.iter_messages(
        source_entity,
        reverse=True,
        min_id=last_forwarded_id
    ):

        if is_sticker(message):
            continue

        msg_hash = hash_message(message)
        if not msg_hash or msg_hash in forwarded_hashes:
            continue

        success = False

        for dest in resolved_destinations:
            try:
                await asyncio.sleep(random.uniform(min_delay, max_delay))

                if message.media:
                    await client.send_file(dest, message.media, caption=message.text or '')
                else:
                    await client.send_message(dest, message.text)

                success = True

            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds + 5)
            except Exception:
                pass

        if success:
            forwarded_hashes.add(msg_hash)
            save_hash(msg_hash)
            save_last_id(message.id)
            forwarded_count += 1

            # 🔥 Mid-run checkpoint
            if forwarded_count % checkpoint_every == 0:
                git_checkpoint()

        if forwarded_count and forwarded_count % pause_every == 0:
            await asyncio.sleep(pause_time)

    print(f"🎉 Done. Forwarded: {forwarded_count}")

try:
    client.loop.run_until_complete(forward_history())
except KeyboardInterrupt:
    print("🛑 Stopped manually.")
