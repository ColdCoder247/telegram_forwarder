import os
import subprocess
import time

# ✅ Always run from repo root
BASE_DIR = os.getcwd()

# ⏱️ Max runtime: 5 hours 30 minutes
START_TIME = time.time()
MAX_RUNTIME = (5 * 60 * 60) + (30 * 60)

# 🔹 Multiple scripts (enable / disable freely)
scripts = [
#    "!! From laptop/𝙿𝚒𝚁𝙰𝙲𝚈 𝚁𝚊𝙲𝙺𝚎𝚃 V6/piracy.py",
#    "!! From laptop/All In ONE ~ TG Files/allinone.py",
#    "!! From laptop/Movie Mania 2.0/moviemania.py",
#    "!! From laptop/Hindi FHD Collections/Hindi FHD Collections.py",
    "!! From laptop/Hindi FHD Movies/Hindi FHD Movies.py",
#    "!! From laptop/Hindi FHD Series/Hindi FHD Series.py",
#    "!! From laptop/FilmXHeaven Uploads/FilmXHeaven Uploads.py",
#    "!! From laptop/CiNE UPLOADS COMBiNATiON/CiNE UPLOADS COMBiNATION.py",
#    "!! From laptop/CiNE UPLOADS MOViES/CiNE UPLOADS MOViES.py",
#    "!! From laptop/CiNE UPLOADS SERiES/CiNE UPLOADS SERiES.py",
#    "!! From laptop/Limited Edition Req Files/Limited Edition Req Files.py",
#    "!! From laptop/moonknight movies/moonmovies.py",
#    "!! From laptop/moonknight series/moonseries.py",
]

# 🔁 Commit function (runs AFTER EACH script)
def commit_txt_files():
    try:
        subprocess.run(
            ["git", "config", "user.name", "github-actions"],
            check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "github-actions@github.com"],
            check=True
        )

        # Add all txt files
        subprocess.run(
            ["git", "add", "**/*.txt"],
            check=True
        )

        # Commit only if something changed
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            check=False
        )

        if result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", "Auto-update progress & logs"],
                check=True
            )
            subprocess.run(["git", "push"], check=True)
            print("💾 Progress committed to GitHub")
        else:
            print("ℹ️ No txt changes to commit")

    except Exception as e:
        print(f"⚠️ Commit failed or skipped: {e}")

# ================= MAIN LOOP =================

for script in scripts:

    # ⏱️ Hard stop if time exceeded
    if time.time() - START_TIME >= MAX_RUNTIME:
        print("⏹️ Time limit reached (5h 30m). Stopping run.")
        break

    script_path = os.path.join(BASE_DIR, script)
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)

    print(f"\n=== Running: {script} ===\n")

    # Skip missing scripts safely
    if not os.path.isfile(script_path):
        print(f"⚠️ Skipped (file not found): {script}")
        continue

    try:
        subprocess.run(
            ["python", script_name],
            cwd=script_dir,
            check=True
        )
        print(f"✅ Finished: {script_name}")

        # ✅ Commit AFTER this script finishes
        commit_txt_files()

    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed: {script_name}\n{e}")

        # Still try to commit whatever progress happened
        commit_txt_files()

    print("⏳ Waiting 60 seconds before next script...\n")
    time.sleep(60)

print("\n🏁 Run finished (completed / skipped / stopped by time limit).")
