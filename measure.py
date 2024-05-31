#!/usr/bin/env python3
# Copyright (c) 2024 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import logging
from typing import List

from components.browser import get_browser_classes_from_str
from components.measurement import MeasurementState
from components.result_map import ResultMap
from components.benchmark_measurement import BenchmarkMeasurement
from components.loading_measurement import LoadingMeasurement
from components.memory_measurement import MemoryMeasurement


def get_measure_by_args(args):
  state = MeasurementState()
  state.low_delays_for_testing = args.low_delays_for_testing
  state.urls = args.urls_file.read().splitlines()

  if args.measure == 'memory':
    return MemoryMeasurement(state)
  if args.measure == 'loading':
    return LoadingMeasurement(state)
  if args.measure == 'benchmarks':
    return BenchmarkMeasurement(state)
  raise RuntimeError(f'No measurement {args.measure} found')

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('measure', type=str)
  parser.add_argument('browser', type=str)
  parser.add_argument('urls_file',
                      type=argparse.FileType('r', encoding='utf-8'),
                      help='File with urls to test')
  parser.add_argument('--connectivity_profile', type=str)
  parser.add_argument('--verbose', action='store_true')
  parser.add_argument('--repeat', type=int, default=1)
  parser.add_argument('--low-delays-for-testing', action='store_true')
  parser.add_argument('--output', type=str, default='results.csv')
  parser.add_argument('--append', action='store_true')
  parser.add_argument('--retry-count', type=int)
  parser.add_argument('-d', '--debug', action='store_true')

  args = parser.parse_args()
  if args.debug:
    args.low_delays_for_testing = True
    args.verbose = True

  log_level = logging.DEBUG if args.verbose else logging.INFO
  log_format = '%(asctime)s: %(message)s'
  logging.basicConfig(level=log_level, format=log_format)

  header = None
  if args.append:
    with open(args.output, 'r', newline='', encoding='utf-8') as result_file:
      header = result_file.read()

  measure = get_measure_by_args(args)
  test_name: str = args.urls_file.name
  repeat: int = args.repeat

  browser_classes = get_browser_classes_from_str(args.browser)
  results = ResultMap()
  final_messages: List[str] = []

  for browser_class in browser_classes:
    browser_name = browser_class().name()
    browser_version = browser_class().get_version()
    logging.info('Testing %s %s', browser_name, browser_version)
    failed_iteration_count = 0
    good_iteration_count = 0
    while good_iteration_count < repeat:
      try:
        metrics = measure.Run(good_iteration_count, browser_class)
        logging.debug([test_name, browser_name, browser_version, metrics])
        for metric, key, value in metrics:
          results.addValue(browser_name, browser_version, metric, key, value)
        good_iteration_count += 1
      except Exception as e:
        failed_iteration_count += 1
        if args.retry_count is not None and failed_iteration_count <= args.retry_count:
          logging.error('Got error %s, retrying', e)
        else:
          final_messages.append(
            f'{test_name}/{browser_name}/{good_iteration_count} failed')
          raise
      results.write_csv(header, args.output)

    for msg in final_messages:
      logging.error(msg)


main()
