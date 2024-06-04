# Copyright (c) 2023 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import json
import os
import logging
import subprocess

from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

from components.browser import Browser
from components.utils import is_win

DEFAULT_CHROME_OPTIONS = [
  '--new-window',
  '--no-default-browser-check',
  '--no-first-run',
  '--password-store=basic',
  '--use-mock-keychain',
  '--disable-features=CalculateNativeWinOcclusion',
  '--remote-debugging-port=9222']


def _get_total_transfer_bytes(har: Dict) -> int:
  total_bytes = 0
  for e in har['log']['entries']:
    res = e['response']
    if hasattr(res, '_transferSize'):
      total_bytes += e['response']['_transferSize']
  return total_bytes


def run_browsertime(browser: Browser, cmd: str, result_dir: str, wait_for_load: bool,
                    extra_args: List[str]) -> List[Tuple[str, Optional[str], float]]:
  npm_binary = 'npm.cmd' if is_win() else 'npm'
  args = ([npm_binary, 'exec', 'browsertime', '--'] +
          ['-b', browser.browsertime_binary] + ['-n', '1'] +
          ['--useSameDir', '--resultDir', f'{result_dir}'] +
          ['--browserRestartTries', '0'] +
          ['--viewPort', 'maximize'] +
          [f'--{browser.browsertime_binary}.binaryPath',
           browser.binary()])
  if not wait_for_load:
    args.extend(['--pageCompleteCheck', 'return true'])
    args.extend(['--pageCompleteCheckStartWait', '15000'])

  args.extend(extra_args)
  args.append('--chrome.noDefaultOptions')
  args.append('--firefox.noDefaultOptions')
  args.append('--firefox.disableBrowsertimeExtension')
  for arg in browser.get_args() + DEFAULT_CHROME_OPTIONS:
    assert arg.startswith('--')
    args.extend(['--chrome.args', arg[2:]])

  args.append(cmd)
  logging.debug(args)
  subprocess.check_call(args)
  output_file = os.path.join(result_dir, 'browsertime.json')
  with open(output_file, 'r', encoding='utf-8') as output:
    output_json = json.load(output)

  results: List[Tuple[str, Optional[str], float]] = []

  har_json = None
  try:
    har_file = os.path.join(result_dir, 'browsertime.har')
    with open(har_file, 'r', encoding='utf-8') as har:
      har_json = json.load(har)
  except FileNotFoundError:
    pass

  for item in output_json:
    url = item['info']['url']
    domain = urlparse(url).netloc
    print(output)
    timings = item['statistics']['timings']
    # results.append(('fullyLoaded', domain, timings['fullyLoaded']['mean']))
    results.append(('firstPaint', domain,
                    timings['firstPaint']['mean']))
    # results.append(('largestContentfulPaint', domain,
    #                 timings['largestContentfulPaint']['renderTime']['mean']))
    results.append(('domContentLoadedTime', domain, timings['pageTimings']['domContentLoadedTime']['mean']))
    results.append(('pageLoadTime', domain, timings['pageTimings']['pageLoadTime']['mean']))

    for extra in item['extras']:
      for metric, value in extra.items():
        if isinstance(value, list):
          for v in value:
            results.append((metric, None, v))
        else:
          results.append((metric, None, float(value)))
  if har_json:
    results.append(('totalBytes', None, _get_total_transfer_bytes(har_json)))
  return results
