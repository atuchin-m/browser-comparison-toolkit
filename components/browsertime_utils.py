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
    if '_transferSize' in res:
      total_bytes += res['_transferSize']
  return total_bytes

def _get_total_bytes(har: Dict) -> int:
  total_bytes = 0
  for e in har['log']['entries']:
    res = e['response']
    if 'bodySize' in res:
      try:
        total_bytes += res['bodySize']
      except:
        pass
    if 'headersSize' in res:
      try:
        total_bytes += res['headersSize']
      except:
        pass
  return total_bytes

def run_browsertime(browser: Browser, cmd: str, result_dir: str, wait_for_load: bool,
                    key: Optional[str], startup_delay: int,
                    extra_args: List[str]) -> List[Tuple[str, Optional[str], float]]:
  assert browser.browsertime_binary is not None

  npm_binary = 'npm.cmd' if is_win() else 'npm'
  args = ([npm_binary, 'exec', 'browsertime', '--'] +
          ['-b', browser.browsertime_binary] + ['-n', '1'] +
          ['--useSameDir', '--resultDir', f'{result_dir}'] +
          ['--browserRestartTries', '0'] +
          ['--viewPort', 'maximize'] +
          [f'--{browser.browsertime_binary}.binaryPath',
           browser.binary()])
  time_to_run = 0
  if not wait_for_load:
    time_to_run = 10 * 1000
    args.extend(['--pageCompleteCheck', 'return true'])
    args.extend(['--pageCompleteCheckStartWait', str(time_to_run)])
    args.extend(['--pageLoadStrategy', 'none'])

  args.extend(extra_args)
  args.extend(['--timeToSettle', str(startup_delay)])
  args.append('--chrome.noDefaultOptions')
  args.append('--firefox.noDefaultOptions')
  args.append('--firefox.disableBrowsertimeExtension')
  args.extend(['--firefox.preference', 'browser.link.open_newwindow:3'])
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

  def get_by_xpath(dict: Optional[Dict], xpath: List[str]):
    if dict is None:
      return None
    if len(xpath) == 0:
      return dict
    key = xpath[0]
    if key in dict:
      return get_by_xpath(dict[key], xpath[1:])
    return None

  max_time = float(15 * 1000)

  for item in output_json:
    if key is None:
      key = item['info']['alias']
      if key is None:
        raise RuntimeError('alias must be set in commands.measure.start(url, alias) ' + cmd)
      if key == 'None':
        key = None
    timings = get_by_xpath(item, ['statistics', 'timings'])
    results.append(('firstPaint', key,
                    get_by_xpath(timings, ['firstPaint', 'median']) or max_time))
    results.append(('largestContentfulPaint', key,
                    get_by_xpath(timings, ['largestContentfulPaint', 'renderTime', 'median']) or max_time))
    results.append(('domContentLoadedTime', key,
                    get_by_xpath(timings, ['pageTimings', 'domContentLoadedTime', 'median']) or max_time))
    results.append(('pageLoadTime', key,
                    get_by_xpath(timings, ['pageTimings', 'pageLoadTime', 'median']) or max_time))
    results.append(('ttfb', key,
                    get_by_xpath(timings, ['ttfb', 'median']) or max_time))

    for extra in item['extras']:
      for metric, value in extra.items():
        if isinstance(value, list):
          for v in value:
            results.append((metric, key, v))
        else:
          results.append((metric, key, float(value)))
  if har_json:
    total_bytes = _get_total_bytes(har_json)
    if total_bytes != 0:
      results.append(('totalBytes', key, total_bytes))
    total_transfer_bytes = _get_total_transfer_bytes(har_json)
    if total_transfer_bytes != 0:
      results.append(('totalTransferredBytes', key, total_transfer_bytes))
  return results
