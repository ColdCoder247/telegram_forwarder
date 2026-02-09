import os
import subprocess
import time

# ✅ Always run from repo root
BASE_DIR = os.getcwd()

# 🔹 Relative paths (Linux + GitHub Actions compatible)
scripts = [
    "!! From laptop/𝙿𝚒𝚁𝙰𝙲𝚈 𝚁𝚊𝙲𝙺𝚎𝚃 V6/piracy.py",
    "!! From laptop/All In ONE ~ TG Files/allinone.py",
    "!! From laptop/Movie Mania 2.0/moviemania.py",
    "!! From laptop/Hindi FHD Collections/Hindi FHD Collections.py",
    "!! From laptop/Hindi FHD Movies/Hindi FHD Movies.py",
    "!! From laptop/Hindi FHD Series/Hindi FHD Series.py",
    "!! From laptop/FilmXHeaven Uploads/FilmXHeaven Uploads.py",
    "!! From laptop/CiNE UPLOADS COMBiNATiON/CiNE UPLOADS COMBiNATION.py",
    "!! From laptop/CiNE UPLOADS MOViES/CiNE UPLOADS MOViES.py",
    "!! From laptop/CiNE UPLOADS SERiES/CiNE UPLOADS SERiES.py",
    "!! From laptop/Limited Edition Req Files/Limited Edition Req Files.py",
    "!! From laptop/moonknight movies/moonmovies.py",
    "!! From laptop/moonknight series/moonseries.py",
]

for script in scripts:
    script_path = os.path.join(BASE_DIR, script)
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)

    print(f"\n=== Running: {script} ===\n")

    # ✅ Skip if file does not exist
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

    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed: {script_name}\n{e}")

    except Exception as e:
        print(f"❌ Unexpected error in {script_name}\n{e}")

    print("⏳ Waiting 60 seconds before next script...\n")
    time.sleep(60)

print("\n🎉 All scripts processed (success + skipped + failed).")
