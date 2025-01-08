# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import platform
import subprocess
import sys
from typing import Iterator, Optional, Tuple


def is_mac():
  return platform.system() == 'Darwin'


def is_win():
  return platform.system() == 'Windows'

def read_urls(urls_file: str, limit: Optional[int] = None) -> Iterator[Tuple[int, str]]:
  with open(urls_file, 'r') as f:
    urls = f.read().splitlines()
    count = 0

    for index, url in enumerate(urls):
      if url.startswith('#') or url.startswith('/'):
        continue
      if url == '':
        break
      if limit is not None and count >= limit:
        break
      yield (index, url)
      count += 1

EXECUTABLE = ".venv/bin/python3"
if sys.platform == "win32":
  EXECUTABLE = ".venv\\Scripts\\python.exe"
if not os.path.exists(EXECUTABLE):
  subprocess.check_call([sys.executable, "install.py"])
