import os
import subprocess
import time

# Always run from repo root
BASE_DIR = os.getcwd()

# Max runtime: 5 hours 30 minutes
START_TIME = time.time()
MAX_RUNTIME = (5 * 60 * 60) + (30 * 60)

# Enable / disable scripts freely
scripts = [
    "!! From laptop/Hindi FHD Movies/Hindi FHD Movies.py",
    # Add more here safely
]

# ================= COMMIT FUNCTION =================

def commit_progress():
    try:
        # Configure Git
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions@github.com"], check=True)

        # Add ALL changes (universal, future-proof)
        subprocess.run(["git", "add", "."], check=True)

        # Check if anything staged
        result = subprocess.run(["git", "diff", "--cached", "--quiet"])

        if result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", "Auto-update Telegram progress"],
                check=True
            )
            subprocess.run(["git", "push"], check=True)
            print("💾 Progress committed successfully")
        else:
            print("ℹ️ No changes to commit")

    except Exception as e:
        print(f"⚠️ Commit skipped or failed: {e}")

# ================= MAIN LOOP =================

for script in scripts:

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
            ["python", script_name],
            cwd=script_dir,
            check=True
        )
        print(f"✅ Finished: {script_name}")

        commit_progress()

    except subprocess.CalledProcessError as e:
        print(f"❌ Script failed: {script_name}\n{e}")
        commit_progress()

    print("⏳ Waiting 60 seconds before next script...\n")
    time.sleep(60)

print("\n🏁 Run finished.")
