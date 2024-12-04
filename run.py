import datetime
import os
import subprocess
import sys

BROWSERS = "Chrome,Brave,Edge,Firefox"
if sys.platform == "darwin":
  BROWSERS += ",Safari"
REPEAT = 10
VERBOSE = True


EXECUTABLE = ".venv/bin/python3"
if sys.platform == "win32":
  EXECUTABLE = ".venv\\Scripts\\python.exe"
if not os.path.exists(EXECUTABLE):
  subprocess.check_call([sys.executable, "install.py"])

platform = sys.platform
if platform == "darwin":
  platform = "mac"

os.makedirs('output', exist_ok=True)
current_date = datetime.datetime.now().strftime("%m-%d-%H-%M")

def run_test(cmd, test, output, browsers=BROWSERS, repeat=REPEAT,):
  args = [EXECUTABLE, "./measure.py", cmd, browsers, test,
          f"--repeat={repeat}",
          "--output", f'output/{platform}-{current_date}-{output}.csv']
  if VERBOSE:
    args.append("--verbose")
  subprocess.run(args)



run_test("script", "scenarios/memory.txt", "mem")
run_test("script", "scenarios/benchmark.txt", "bench")
run_test("loading", "scenarios/new-list-v2.txt", "loading")
