import subprocess
import sys

EXECUTABLE = ".venv/bin/python3"
if sys.platform == "win32":
  EXECUTABLE = ".venv\\Scripts\\python.exe"

npm = "npm.cmd" if sys.platform == "win32" else "npm"
subprocess.check_call([npm, 'install', 'browsertime', 'execa'])
subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
subprocess.check_call([EXECUTABLE, "-m", "pip", "install", "psutil", "pandas", "matplotlib"])
