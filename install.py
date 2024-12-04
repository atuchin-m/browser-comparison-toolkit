import subprocess
import sys

subprocess.check_call(['npm', 'install', 'browsertime', 'execa'])
subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
subprocess.check_call([".venv/bin/python3", "-m", "pip", "install", "psutil", "pandas", "matplotlib"])
