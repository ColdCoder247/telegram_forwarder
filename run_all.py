import os
import subprocess
import time
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# ================= CONFIG =================

BASE_DIR = os.getcwd()

# Max runtime: 5 hours 30 minutes
START_RUNTIME = time.time()
MAX_RUNTIME = (5 * 60 * 60) + (30 * 60)

# IST Timezone
IST = ZoneInfo("Asia/Kolkata")

# Telegram Credentials (Add in GitHub Secrets)
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
CHAT_ID = os.getenv("TG_CHAT_ID")

# Enable / disable scripts freely
scripts = [
    "!! From laptop/𝙿𝚒𝚁𝙰𝙲𝚈 𝚁𝚊𝙲𝙺𝚎𝚃 V6/piracy.py",
    "!! From laptop/All In ONE ~ TG Files/allinone.py",
    "!! From laptop/Moonknight  Drama/moonknightdrama.py",
    "!! From laptop/Hindi FHD Collections/Hindi FHD Collections.py",
    "!! From laptop/Hindi FHD Movies/Hindi FHD Movies.py",
    "!! From laptop/Hindi FHD Series/Hindi FHD Series.py",
    "!! From laptop/Limited Edition Req Files/Limited Edition Req Files.py",
    "!! From laptop/moonknight movies/moonmovies.py",
    "!! From laptop/moonknight series/moonseries.py",
]

# ================= TELEGRAM FUNCTION =================

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        requests.post(url, data=payload, timeout=15)
    except Exception as e:
        print("Telegram send failed:", e)

# ================= HELPER FUNCTION =================

def format_duration(seconds):
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# ================= START GLOBAL =================

global_start = datetime.now(IST)

send_telegram(
    f"🚀 <b>Run Started</b>\n\n"
    f"🕒 {global_start.strftime('%d-%m-%Y %I:%M:%S %p IST')}"
)

# ================= MAIN LOOP =================

for script in scripts:

    # Stop if time exceeded
    if time.time() - START_RUNTIME >= MAX_RUNTIME:
        now_ist = datetime.now(IST)
        send_telegram(
            f"⏹️ <b>Time Limit Reached</b>\n\n"
            f"🕒 {now_ist.strftime('%d-%m-%Y %I:%M:%S %p IST')}"
        )
        break

    script_path = os.path.join(BASE_DIR, script)
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)

    print(f"\n=== Running: {script} ===\n")

    if not os.path.isfile(script_path):
        send_telegram(f"⚠️ <b>File Not Found:</b> {script_name}")
        continue

    start_time = datetime.now(IST)
    start_timer = time.time()

    try:
        result = subprocess.run(
            ["python3", script_name],
            cwd=script_dir,
            capture_output=True,
            text=True
        )

        end_time = datetime.now(IST)
        duration_seconds = time.time() - start_timer
        duration_str = format_duration(duration_seconds)

        start_str = start_time.strftime("%d-%m-%Y %I:%M:%S %p IST")
        end_str = end_time.strftime("%d-%m-%Y %I:%M:%S %p IST")

        # Limit logs to avoid Telegram 4096 character limit
        logs = (result.stdout + "\n" + result.stderr)[-3500:]

        if result.returncode == 0:
            message = (
                f"✅ <b>Script Completed</b>\n\n"
                f"📂 {script_name}\n\n"
                f"🕒 Start: {start_str}\n"
                f"🕒 End: {end_str}\n"
                f"⏱ Duration: {duration_str}\n\n"
                f"📝 Logs:\n<pre>{logs}</pre>"
            )
        else:
            message = (
                f"❌ <b>Script Failed</b>\n\n"
                f"📂 {script_name}\n\n"
                f"🕒 Start: {start_str}\n"
                f"🕒 End: {end_str}\n"
                f"⏱ Duration: {duration_str}\n\n"
                f"⚠️ Error Logs:\n<pre>{logs}</pre>"
            )

        send_telegram(message)

    except Exception as e:
        send_telegram(f"❌ <b>Critical Error in {script_name}</b>\n\n{str(e)}")

    print("⏳ Waiting 60 seconds before next script...\n")
    time.sleep(60)

# ================= FINAL SUMMARY =================

global_end = datetime.now(IST)
total_runtime = format_duration(time.time() - START_RUNTIME)

send_telegram(
    f"🏁 <b>All Scripts Finished</b>\n\n"
    f"🕒 Started: {global_start.strftime('%d-%m-%Y %I:%M:%S %p IST')}\n"
    f"🕒 Ended: {global_end.strftime('%d-%m-%Y %I:%M:%S %p IST')}\n"
    f"⏱ Total Runtime: {total_runtime}"
)

print("\n🏁 Run finished.")
