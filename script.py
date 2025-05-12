import subprocess

for i in range(2):
    print(f"🔁 Lancement de la partie {i + 1}... (appuie sur Q pour quitter quand terminé)")
    subprocess.run(["python", "PacMan.py"])