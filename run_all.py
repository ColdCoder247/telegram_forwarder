import os
import subprocess
import time

# Always run from repo root
BASE_DIR = os.getcwd()

# ⏱️ Max runtime: 5 hours 30 minutes
START_TIME = time.time()
MAX_RUNTIME = (5 * 60 * 60) + (30 * 60)

# Enable / disable scripts freely
scripts = [
    "!! From laptop/Hindi FHD Movies/Hindi FHD Movies.py",
    "!! From laptop/Mu - HiNDI ORIGINΔL/muhindioriginal.py",
    "!! From laptop/Mu - Original  Copyright/muoriginalcopy.py",
    "!! From laptop/PIRATES/pirates.py",
    "!! From laptop/PIRATES ~ MOVIES DUMP v3/pirates.py",
    "!! From laptop/PIRATES ~ TV SERIES/pirateseries.py",
    "!! From laptop/Statesman/statesman.py",
    "!! From laptop/𝙿𝚒𝚁𝙰𝙲𝚈 𝚁𝚊𝙲𝙺𝚎𝚃 V6/piracy.py",
    "!! From laptop\BOB 𝐂𝐨𝐦𝐛𝐢𝐧𝐚𝐭𝐢𝐨𝐧 2.1\bobcombination.py",
    "!! From laptop\All In ONE ~ TG Files\allinone.py",
    "!! From laptop\Moonknight  Drama\moonknightdrama.py",
    "!! From laptop\Movie Mania 2.0\moviemania.py",
    "!! From laptop\Hindi FHD Collections\Hindi FHD Collections.py",
    "!! From laptop\Hindi FHD Movies\Hindi FHD Movies.py",
    "!! From laptop\Hindi FHD Series\Hindi FHD Series.py",
    "!! From laptop\FilmXHeaven Uploads\FilmXHeaven Uploads.py",
    "!! From laptop\CiNE UPLOADS COMBiNATiON\CiNE UPLOADS COMBiNATION.py",
    "!! From laptop\CiNE UPLOADS MOViES\CiNE UPLOADS MOViES.py",
    "!! From laptop\CiNE UPLOADS SERiES\CiNE UPLOADS SERiES.py",
    "!! From laptop\Limited Edition Req Files\Limited Edition Req Files.py",
    "!! From laptop\moonknight movies\moonmovies.py",
    "!! From laptop\moonknight series\moonseries.py",
]

# ================= MAIN LOOP =================

for script in scripts:

    # Stop if time exceeded
    if time.time() - START_TIME >= MAX_RUNTIME:
        print("⏹️ Time limit reached. Stopping run.")
        break

    script_path = os.path.join(BASE_DIR, script)
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)

    print(f"\n=== Running: {script} ===\n")

    if not os.path.isfile(script_path):
        print(f"⚠️ Skipped (file not found): {script}")
        continue

    try:
        subprocess.run(
            ["python3", script_name],
            cwd=script_dir,
            check=True
        )
        print(f"✅ Finished: {script_name}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed: {script_name}\n{e}")

    print("⏳ Waiting 60 seconds before next script...\n")
    time.sleep(60)

print("\n🏁 Run finished.")
