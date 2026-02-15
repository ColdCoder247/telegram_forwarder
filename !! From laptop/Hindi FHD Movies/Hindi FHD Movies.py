import asyncio
import os
import random
from telethon import TelegramClient, errors
from hashlib import md5
from datetime import datetime

# ==============================
# 🔹 CONFIG
# ==============================

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")

source_group = -1002394425543
destination_groups = ['@JK_HDSGIJ_HPUHSA_mfdgsdgjkhiuahs']

channel = "Hindi FHD Movies"

min_delay = 8
max_delay = 15

pause_every = 35
pause_time = 300

hashes_file = 'forwarded_hashes.txt'
log_file = 'forward_log.txt'
duplicates_file = 'duplicates_log.txt'
resume_file = 'last_message_id.txt'

forwarded_hashes = set()

client = TelegramClient('forward_session', api_id, api_hash)


# ==============================
# 🔹 HELPER FUNCTIONS
# ==============================

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


# ==============================
# 🔹 MAIN LOGIC
# ==============================

async def forward_history():
    load_hashes()
    await client.start()

    print("✅ Bot started")

    source_entity = await client.get_input_entity(source_group)

    resolved_destinations = []
    for dest in destination_groups:
        entity = await client.get_entity(dest)
        resolved_destinations.append(entity)

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

        for dest in resolved_destinations:
            try:
                await asyncio.sleep(random.uniform(min_delay, max_delay))

                # ✅ NOT forward → resend
                if message.media:
                    await client.send_file(
                        dest,
                        message.media,
                        caption=message.text or ''
                    )
                else:
                    await client.send_message(dest, message.text)

                log(log_file, f"Sent to {dest.id}")
                print(f"✅ Sent: {message.id}")

                save_last_id(message.id)
                forwarded_count += 1

            except errors.FloodWaitError as e:
                print(f"⏳ Flood wait: {e.seconds}")
                await asyncio.sleep(e.seconds + 5)

            except Exception as e:
                print(f"❌ Error: {e}")

        forwarded_hashes.add(msg_hash)
        save_hash(msg_hash)

        if forwarded_count % pause_every == 0:
            print("⏸ Auto pause...")
            await asyncio.sleep(pause_time)

    print("🎉 Done.")


# ==============================
# 🔹 RUN
# ==============================

client.loop.run_until_complete(forward_history())
