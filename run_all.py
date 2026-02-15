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
    # Add more scripts here safely
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
