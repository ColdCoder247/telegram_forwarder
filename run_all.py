import os
import subprocess
import time

# 🔹 Add the full paths of your Python scripts here
scripts = [
#   r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Mu - HiNDI ORIGINΔL\muhindioriginal.py",
#   r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Mu - Original  Copyright\muoriginalcopy.py",
#   r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\PIRATES\pirates.py",
#   r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\PIRATES ~ MOVIES DUMP v3\pirates.py",
#   r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\PIRATES ~ TV SERIES\pirateseries.py",
#   r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Statesman\statesman.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\𝙿𝚒𝚁𝙰𝙲𝚈 𝚁𝚊𝙲𝙺𝚎𝚃 V6\piracy.py",
#   r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\BOB 𝐂𝐨𝐦𝐛𝐢𝐧𝐚𝐭𝐢𝐨𝐧 2.1\bobcombination.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\All In ONE ~ TG Files\allinone.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Moonknight  Drama\moonknightdrama.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Movie Mania 2.0\moviemania.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Hindi FHD Collections\Hindi FHD Collections.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Hindi FHD Movies\Hindi FHD Movies.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Hindi FHD Series\Hindi FHD Series.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\FilmXHeaven Uploads\FilmXHeaven Uploads.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\CiNE UPLOADS COMBiNATiON\CiNE UPLOADS COMBiNATION.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\CiNE UPLOADS MOViES\CiNE UPLOADS MOViES.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\CiNE UPLOADS SERiES\CiNE UPLOADS SERiES.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\Limited Edition Req Files\Limited Edition Req Files.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\moonknight movies\moonmovies.py",
    r"C:\Users\OpenShift\Desktop\telegram_forwarder\!! From laptop\moonknight series\moonseries.py",
]

for script in scripts:
    script_dir = os.path.dirname(script)
    script_name = os.path.basename(script)

    print(f"\n=== Running: {script} ===\n")

    try:
        # Run the script inside its own folder (so local imports/files work)
        subprocess.run(["python", script_name], cwd=script_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error while running {script}: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

    # 🔹 Delay before next script
    print("⏳ Waiting 60 seconds before running the next script...\n")
    time.sleep(60)

print("\n✅ All scripts finished (with or without errors).")
