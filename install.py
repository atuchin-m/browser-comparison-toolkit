import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
subprocess.check_call([".venv/bin/python3", "-m", "pip", "install", "-r", "requirements.txt"])
