import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

with open("./requirements.txt") as f:
	packages = f.read().strip().split("\n")

print("installing:",packages)
for p in packages:
	install(p)

