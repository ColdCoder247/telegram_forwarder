```python
import asyncio
import os
import random
import subprocess
from datetime import datetime

from telethon import TelegramClient, errors
from telethon.sessions import StringSession


# ============================================================
# CONFIG
# ============================================================

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")
string_session = os.getenv("TG_STRING_SESSION")

source_group = "-1002051140912"

destination_groups = [
    "@akdiuyebcmalkdjkdiuqagbfd"
]

channel = "Lossless Community ❤️🔥"

# Delay between sending files
min_delay = 8
max_delay = 15

# Long pause after this many successfully copied audio files
pause_every = 35
pause_time = 300

# Progress files
processed_file = "forwarded_hashes.txt"
log_file = "forward_log.txt"
duplicates_file = "duplicates_log.txt"
resume_file = "last_message_id.txt"


# ============================================================
# SUPPORTED AUDIO FORMATS
# ============================================================

# Lossless formats:
# FLAC  - Free Lossless Audio Codec
# ALAC  - Apple Lossless
# WAV   - PCM/WAVE
# AIFF  - Apple/Audio Interchange File Format
# APE   - Monkey's Audio
# WV    - WavPack
# TTA   - True Audio
#
# Common compressed audio:
# MP3
# M4A   - may contain ALAC or AAC
# AAC
# OGG
# OPUS
# WMA
#
# Note:
# M4A is a container and can contain either ALAC (lossless)
# or AAC (lossy), so it is included intentionally.

SUPPORTED_AUDIO_EXTENSIONS = {
    ".flac",
    ".alac",
    ".m4a",
    ".mp3",
    ".wav",
    ".wave",
    ".aiff",
    ".aif",
    ".ape",
    ".wv",
    ".tta",
    ".aac",
    ".ogg",
    ".opus",
    ".wma",
}


# ============================================================
# TELEGRAM CLIENT
# ============================================================

client = TelegramClient(
    StringSession(string_session),
    api_id,
    api_hash
)


# ============================================================
# PROCESSED MESSAGE IDs
# ============================================================

processed_ids = set()


def load_processed_ids():
    """
    Load already processed Telegram message IDs.
    """

    if not os.path.exists(processed_file):
        return

    try:
        with open(
            processed_file,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:

                line = line.strip()

                if line:
                    processed_ids.add(int(line))

    except Exception as e:

        print("Error loading processed IDs:", e)


def save_processed_id(message_id):

    """
    Save a successfully processed message ID.
    """

    with open(
        processed_file,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"{message_id}\n"
        )


# ============================================================
# LOGGING
# ============================================================

def log(file_name, message):

    with open(
        file_name,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"[{datetime.now()}] {message}\n"
        )


# ============================================================
# RESUME
# ============================================================

def load_last_id():

    if not os.path.exists(resume_file):
        return 0

    try:

        with open(
            resume_file,
            "r",
            encoding="utf-8"
        ) as f:

            value = f.read().strip()

            if value:
                return int(value)

    except Exception as e:

        print("Error loading last message ID:", e)

    return 0


def save_last_id(message_id):

    with open(
        resume_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            str(message_id)
        )


# ============================================================
# GIT SAFE COMMIT
# ============================================================

def safe_commit():

    try:

        subprocess.run(
            [
                "git",
                "config",
                "--global",
                "user.name",
                "github-actions"
            ],
            check=False
        )

        subprocess.run(
            [
                "git",
                "config",
                "--global",
                "user.email",
                "actions@github.com"
            ],
            check=False
        )

        subprocess.run(
            [
                "git",
                "add",
                resume_file,
                processed_file,
                log_file,
                duplicates_file
            ],
            check=False
        )

        result = subprocess.run(
            [
                "git",
                "diff",
                "--cached",
                "--quiet"
            ],
            check=False
        )

        # return code 1 = changes exist
        if result.returncode != 0:

            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    "Auto update progress"
                ],
                check=True
            )

            subprocess.run(
                [
                    "git",
                    "push"
                ],
                check=True
            )

            print("💾 Progress committed")

        else:

            print("ℹ️ Nothing to commit")

    except Exception as e:

        print(
            "Commit error:",
            repr(e)
        )


# ============================================================
# CHECK SUPPORTED AUDIO
# ============================================================

def is_supported_audio(message):
    """
    Returns True if the Telegram message contains a file
    with a supported audio extension.
    """

    if not message.file:
        return False

    filename = message.file.name

    if not filename:
        return False

    filename = filename.lower()

    return any(
        filename.endswith(extension)
        for extension in SUPPORTED_AUDIO_EXTENSIONS
    )


# ============================================================
# GET AUDIO TYPE
# ============================================================

def get_audio_extension(message):

    if not message.file or not message.file.name:
        return "unknown"

    filename = message.file.name.lower()

    for extension in SUPPORTED_AUDIO_EXTENSIONS:

        if filename.endswith(extension):
            return extension

    return "unknown"


# ============================================================
# COPY AUDIO AS NEW MESSAGE
# ============================================================

async def copy_audio(destination, message):

    """
    Send Telegram media as a NEW message.

    IMPORTANT:
    We use send_file() instead of forward_messages().

    Therefore Telegram will NOT display:

        Forwarded from Lossless Community ❤️🔥

    We intentionally do NOT use force_document=True so that
    Telegram can preserve/display supported audio as audio
    rather than forcing it into a generic document.
    """

    caption = message.text or None

    await client.send_file(
        destination,
        message.media,
        caption=caption
    )


# ============================================================
# MAIN
# ============================================================

async def forward_history():

    load_processed_ids()

    print(
        f"Loaded {len(processed_ids)} processed message IDs"
    )

    await client.start()

    print("✅ Telegram client started")

    # --------------------------------------------------------
    # SOURCE
    # --------------------------------------------------------

    source_entity = await client.get_input_entity(
        int(source_group)
    )

    # --------------------------------------------------------
    # DESTINATIONS
    # --------------------------------------------------------

    resolved_destinations = []

    for destination in destination_groups:

        try:

            entity = await client.get_entity(
                destination
            )

            resolved_destinations.append(entity)

            print(
                f"✅ Destination resolved: {destination}"
            )

        except Exception as e:

            print(
                f"❌ Could not resolve destination {destination}:",
                e
            )

    if not resolved_destinations:

        print(
            "❌ No valid destination groups."
        )

        return

    # --------------------------------------------------------
    # START MESSAGE
    # --------------------------------------------------------

    last_id = load_last_id()

    print(
        f"▶️ Resuming from message ID: {last_id}"
    )

    copied_count = 0
    scanned_count = 0

    # --------------------------------------------------------
    # SEND START MESSAGE
    # --------------------------------------------------------

    for destination in resolved_destinations:

        try:

            await client.send_message(
                destination,
                f"===== Started {channel} ====="
            )

        except Exception as e:

            print(
                "Start message error:",
                e
            )

    # ========================================================
    # READ SOURCE HISTORY
    # ========================================================

    async for message in client.iter_messages(
        source_entity,
        reverse=True,
        min_id=last_id
    ):

        scanned_count += 1

        # ----------------------------------------------------
        # ALREADY PROCESSED
        # ----------------------------------------------------

        if message.id in processed_ids:

            log(
                duplicates_file,
                f"Already processed message {message.id}"
            )

            # Move resume position forward
            save_last_id(message.id)

            continue

        # ----------------------------------------------------
        # NOT SUPPORTED AUDIO
        # ----------------------------------------------------

        if not is_supported_audio(message):

            filename = None

            if message.file:
                filename = message.file.name

            print(
                f"⏭️ Skipping message {message.id} - "
                f"unsupported file: {filename}"
            )

            log(
                log_file,
                f"Skipped message {message.id} - "
                f"unsupported file: {filename}"
            )

            # Move resume position even for skipped messages
            save_last_id(message.id)

            continue

        # ----------------------------------------------------
        # AUDIO INFORMATION
        # ----------------------------------------------------

        filename = message.file.name

        file_size = message.file.size or 0

        extension = get_audio_extension(message)

        print(
            "\n🎵 Supported audio found"
        )

        print(
            f"   Message ID : {message.id}"
        )

        print(
            f"   Filename   : {filename}"
        )

        print(
            f"   Format     : {extension}"
        )

        print(
            f"   Size       : {file_size / (1024 * 1024):.2f} MB"
        )

        # ----------------------------------------------------
        # COPY TO EVERY DESTINATION
        # ----------------------------------------------------

        message_success = True

        for destination in resolved_destinations:

            try:

                # Random delay
                delay = random.uniform(
                    min_delay,
                    max_delay
                )

                print(
                    f"⏳ Waiting {delay:.1f} seconds..."
                )

                await asyncio.sleep(delay)

                # ------------------------------------------------
                # SEND AS NEW MESSAGE
                # ------------------------------------------------

                await copy_audio(
                    destination,
                    message
                )

                print(
                    f"✅ Copied as NEW message: {filename}"
                )

                log(
                    log_file,
                    f"Copied NEW AUDIO "
                    f"{message.id} - "
                    f"{filename}"
                )

            except errors.FloodWaitError as e:

                print(
                    f"⚠️ Telegram FloodWait: "
                    f"{e.seconds} seconds"
                )

                log(
                    log_file,
                    f"FloodWait {e.seconds}s "
                    f"on message {message.id}"
                )

                await asyncio.sleep(
                    e.seconds + 5
                )

                # Retry once after FloodWait
                try:

                    await copy_audio(
                        destination,
                        message
                    )

                    print(
                        f"✅ Retry successful: {filename}"
                    )

                except Exception as retry_error:

                    print(
                        "❌ Retry failed:",
                        retry_error
                    )

                    log(
                        log_file,
                        f"Retry failed for "
                        f"{message.id}: "
                        f"{retry_error}"
                    )

                    message_success = False

            except errors.RPCError as e:

                print(
                    f"❌ Telegram error for {filename}:",
                    e
                )

                log(
                    log_file,
                    f"Telegram error "
                    f"{message.id}: {e}"
                )

                message_success = False

            except Exception as e:

                print(
                    f"❌ Error copying {filename}:",
                    e
                )

                log(
                    log_file,
                    f"Error copying "
                    f"{message.id} "
                    f"{filename}: {e}"
                )

                message_success = False

        # ----------------------------------------------------
        # ONLY MARK COMPLETE IF ALL DESTINATIONS SUCCEEDED
        # ----------------------------------------------------

        if message_success:

            copied_count += 1

            processed_ids.add(
                message.id
            )

            save_processed_id(
                message.id
            )

            save_last_id(
                message.id
            )

            print(
                f"💾 Progress saved: {message.id}"
            )

            # ------------------------------------------------
            # PERIODIC GIT COMMIT
            # ------------------------------------------------

            if copied_count % 15 == 0:

                print(
                    "💾 Performing periodic Git commit..."
                )

                safe_commit()

            # ------------------------------------------------
            # LONG PAUSE
            # ------------------------------------------------

            if copied_count % pause_every == 0:

                print(
                    f"\n⏸️ {copied_count} audio files copied."
                )

                print(
                    f"⏸️ Pausing for {pause_time} seconds..."
                )

                await asyncio.sleep(
                    pause_time
                )

                print(
                    "▶️ Resuming..."
                )

        else:

            print(
                f"⚠️ Message {message.id} was NOT marked complete."
            )

            print(
                "It will be retried on the next run."
            )

    # ========================================================
    # FINISHED
    # ========================================================

    for destination in resolved_destinations:

        try:

            await client.send_message(
                destination,
                f"===== Till Now Done {channel} =====\n"
                f"Audio files copied: {copied_count}"
            )

        except Exception as e:

            print(
                "Finish message error:",
                e
            )

    # Final Git commit
    safe_commit()

    print(
        "\n========================================"
    )

    print(
        "✅ Finished"
    )

    print(
        f"📂 Messages scanned : {scanned_count}"
    )

    print(
        f"🎵 Audio copied     : {copied_count}"
    )

    print(
        "========================================"
    )


# ============================================================
# RUN
# ============================================================

try:

    client.loop.run_until_complete(
        forward_history()
    )

except KeyboardInterrupt:

    print(
        "\n🛑 Stopped by user"
    )

    safe_commit()

except Exception as e:

    print(
        "\n❌ Fatal error:",
        repr(e)
    )

    safe_commit()
```
