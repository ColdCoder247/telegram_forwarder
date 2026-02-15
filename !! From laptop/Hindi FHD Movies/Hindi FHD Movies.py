import os
import asyncio
import time
import subprocess
from telethon import TelegramClient

# ==============================
# 🔹 CONFIG
# ==============================

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")

source_channel = -1002394425543
target_channel = '@JK_HDSGIJ_HPUHSA_mfdgsdgjkhiuahs'

progress_file = "last_message_id.txt"

# ⏱️ GitHub safe limit
START_TIME = time.time()
MAX_RUNTIME = (5 * 60 * 60) + (30 * 60)


# ==============================
# 🔹 SAVE PROGRESS FUNCTION
# ==============================

def save_progress(message_id):
    try:
        with open(progress_file, "w") as f:
            f.write(str(message_id))

        subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])
        subprocess.run(["git", "add", progress_file])
        subprocess.run(["git", "commit", "-m", f"Checkpoint {message_id}"], check=False)
        subprocess.run(["git", "push"], check=False)

        print(f"✅ Checkpoint saved at {message_id}")

    except Exception as e:
        print(f"⚠️ Git push failed: {e}")


# ==============================
# 🔹 MAIN LOGIC
# ==============================

async def main():
    client = TelegramClient("session", api_id, api_hash)
    await client.start()

    # 🔹 Load last saved ID safely
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            try:
                last_id = int(f.read().strip())
            except:
                last_id = 0
    else:
        # 🔥 FIRST RUN PROTECTION
        last_msg = await client.get_messages(source_channel, limit=1)
        last_id = last_msg[0].id if last_msg else 0

        with open(progress_file, "w") as f:
            f.write(str(last_id))

        print(f"🆕 First run detected. Starting from latest ID: {last_id}")
        await client.disconnect()
        return

    print(f"🔁 Resuming from ID: {last_id}")

    counter = 0
    latest_processed_id = last_id

    # 🔥 Proper min_id usage + correct order
    async for message in client.iter_messages(
            source_channel,
            min_id=last_id,
            reverse=True
    ):

        # ⏰ Stop if time exceeded
        if time.time() - START_TIME > MAX_RUNTIME:
            print("⏰ Time limit reached. Saving progress...")
            save_progress(latest_processed_id)
            break

        try:
            await client.forward_messages(target_channel, message)
            latest_processed_id = message.id
            counter += 1

            print(f"➡️ Forwarded: {message.id}")

            await asyncio.sleep(2)

            # 🔥 Checkpoint every 15 messages
            if counter % 15 == 0:
                save_progress(latest_processed_id)

        except Exception as e:
            print(f"⚠️ Error forwarding {message.id}: {e}")
            await asyncio.sleep(5)

    # Final save before exit
    if latest_processed_id != last_id:
        save_progress(latest_processed_id)

    await client.disconnect()
    print("✅ Script finished safely.")


# ==============================
# 🔹 RUN
# ==============================

asyncio.run(main())
