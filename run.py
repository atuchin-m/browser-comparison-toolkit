#! /usr/bin/env python3
import datetime
import os
import subprocess
import sys

from components.utils import EXECUTABLE


BROWSERS = "Chrome,Brave,Edge,Firefox"
if sys.platform == "darwin":
  BROWSERS += ",Safari"
REPEAT = 10
VERBOSE = True
PREFIX = ""

# BROWSERS = "Chrome,Brave"

platform = sys.platform
if platform == "darwin":
  platform = "mac"

os.makedirs('output', exist_ok=True)

def run_test(cmd: str, test: str, output: str, browsers: str = BROWSERS, repeat: int = REPEAT):
  current_date = datetime.datetime.now().strftime("%m-%d %H-%M")
  args = [EXECUTABLE, "./measure.py", cmd, browsers, test,
          f"--repeat={repeat}",
          "--output", f'output/{PREFIX}-{platform}-{current_date}-{output}.csv']
  if VERBOSE:
    args.append("--verbose")
  subprocess.run(args)


run_test("script", "scripts/memory.mjs", "memory")
run_test("memory", "scenarios/new-list-v3.txt", "memory-ddg")

run_test("script", "scripts/multipage.mjs", "loading-multipage", "Brave,Edge,Chrome",5)
run_test("script", "scripts/multipage.mjs", "loading-multipage", "Safari",5)
run_test("script", "scripts/multipage.mjs", "loading-multipage", "Firefox",5)


# run_test("script", "scripts/speedometer3.mjs", "bench-speedometer3")
# run_test("script", "scripts/jetstream.mjs", "bench-jetstream")
# run_test("script", "scripts/motionmark.mjs", "bench-motionmark")
