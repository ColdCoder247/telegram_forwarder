import asyncio
import os
import random
import subprocess

from telethon import TelegramClient, errors
from telethon.sessions import StringSession

from hashlib import md5
from datetime import datetime

# ================= CONFIG =================

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")
string_session = os.getenv("TG_STRING_SESSION")

source_group = '-1002051140912'

destination_groups = [
    '@akdiuyebcmalkdjkdiuqagbfd'
]

channel = "Lossless Community ❤️🔥"

min_delay = 8
max_delay = 15

pause_every = 35
pause_time = 300

hashes_file = "forwarded_hashes.txt"
log_file = "forward_log.txt"
duplicates_file = "duplicates_log.txt"
resume_file = "last_message_id.txt"

forwarded_hashes = set()

client = TelegramClient(
    StringSession(string_session),
    api_id,
    api_hash
)

# ================= SAFE COMMIT =================

def safe_commit():

    try:

        subprocess.run(
            ["git","config","--global","user.name","github-actions"]
        )

        subprocess.run(
            ["git","config","--global","user.email","actions@github.com"]
        )

        subprocess.run(
            ["git","add",
             resume_file,
             hashes_file,
             log_file,
             duplicates_file]
        )

        result = subprocess.run(
            ["git","diff","--cached","--quiet"]
        )

        if result.returncode != 0:

            subprocess.run(
                ["git","commit","-m","Auto update progress"],
                check=True
            )

            subprocess.run(
                ["git","push"],
                check=True
            )

            print("💾 Progress committed")

        else:

            print("ℹ️ Nothing to commit")

    except Exception as e:

        print("Commit error:",e)

# ================= HELPERS =================

def load_hashes():

    if os.path.exists(hashes_file):

        with open(
                hashes_file,
                "r",
                encoding="utf-8"
        ) as f:

            for line in f:

                forwarded_hashes.add(
                    line.strip()
                )

def save_hash(msg_hash):

    with open(
            hashes_file,
            "a",
            encoding="utf-8"
    ) as f:

        f.write(
            msg_hash+"\n"
        )

def log(file,msg):

    with open(
            file,
            "a",
            encoding="utf-8"
    ) as f:

        f.write(
            f"[{datetime.now()}] {msg}\n"
        )

def hash_message(message):

    if message.grouped_id:

        return f"group_{message.grouped_id}"

    if message.text:

        return md5(
            message.text.encode(
                "utf-8"
            )
        ).hexdigest()

    if message.media:

        return f"{message.id}"

    return None

def load_last_id():

    if os.path.exists(
            resume_file
    ):

        with open(
                resume_file,
                "r"
        ) as f:

            return int(
                f.read().strip()
            )

    return 0

def save_last_id(msg_id):

    with open(
            resume_file,
            "w"
    ) as f:

        f.write(
            str(msg_id)
        )

# ================= MAIN =================

async def forward_history():

    load_hashes()

    await client.start()

    print("Bot started")

    source_entity = await client.get_input_entity(
        int(source_group)
    )

    resolved_destinations=[]

    for dest in destination_groups:

        entity=await client.get_entity(
            dest
        )

        resolved_destinations.append(
            entity
        )

    for d in resolved_destinations:

        await client.send_message(
            d,
            f"===== Started {channel}"
        )

    last_id=load_last_id()

    forwarded_count=0

    async for message in client.iter_messages(
            source_entity,
            reverse=True,
            min_id=last_id
    ):

        msg_hash=hash_message(
            message
        )

        if not msg_hash:

            continue

        if msg_hash in forwarded_hashes:

            log(
                duplicates_file,
                f"duplicate {message.id}"
            )

            continue

        for dest in resolved_destinations:

            try:

                await asyncio.sleep(
                    random.uniform(
                        min_delay,
                        max_delay
                    )
                )

                # ===================
                # MEDIA GROUP / ALBUM
                # ===================

                if message.grouped_id:

                    album=await client.get_messages(
                        source_entity,
                        min_id=message.id-20,
                        max_id=message.id+20
                    )

                    album_msgs=[
                        m for m in album
                        if m.grouped_id==message.grouped_id
                    ]

                    await client.forward_messages(
                        dest,
                        album_msgs,
                        source_entity
                    )

                    print(
                        f"Album forwarded {message.grouped_id}"
                    )

                # ===================
                # NORMAL MESSAGE
                # ===================

                else:

                    await client.forward_messages(
                        dest,
                        message,
                        source_entity
                    )

                    print(
                        f"Forwarded {message.id}"
                    )

                forwarded_count+=1

                log(
                    log_file,
                    f"forwarded {message.id}"
                )

                save_last_id(
                    message.id
                )

                if forwarded_count%15==0:

                    safe_commit()

            except errors.FloodWaitError as e:

                print(
                    "Flood wait",
                    e.seconds
                )

                await asyncio.sleep(
                    e.seconds+5
                )

            except Exception as e:

                print(
                    "Error",
                    e
                )

                log(
                    log_file,
                    str(e)
                )

        forwarded_hashes.add(
            msg_hash
        )

        save_hash(
            msg_hash
        )

        if forwarded_count!=0 and \
           forwarded_count%pause_every==0:

            print(
                "Pausing..."
            )

            await asyncio.sleep(
                pause_time
            )

    for d in resolved_destinations:

        await client.send_message(
            d,
            f"Till Now Done {channel}"
        )

    safe_commit()

    print(
        "Finished",
        forwarded_count
    )

# ================= RUN =================

try:

    client.loop.run_until_complete(
        forward_history()
    )

except KeyboardInterrupt:

    print(
        "Stopped"
    )
