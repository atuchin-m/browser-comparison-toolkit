#!/usr/bin/env python3
# Copyright (c) 2024 The Brave Authors. All rights reserved.
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at https://mozilla.org/MPL/2.0/.

import csv
import statistics

from typing import Dict, List, Optional, Tuple

class ResultMap():
  #  Dict[Tuple[metric, key, browser_spec], metric_values]
  _map: Dict[Tuple[str, Optional[str], str, str], List[float]] = {}
  _error: Dict[Tuple[str, Optional[str], str, str], float] = {}

  def addValue(self, browser: str, version: str, metric: str, key: Optional[str],
               value: float):
    s = metric.split('#error')
    if len(s) > 1:
      original_metric = s[0]
      index = (original_metric, key, browser, version)
      assert self._error.get(index) is None
      self._error[index] = value
    else:
      index = (metric, key, browser, version)
      self._map.setdefault(index, [])
      self._map[(metric, key, browser, version)].append(value)

  # Calculate *_Total metrics
  def calc_total_metrics(self):
    for (metric, key, browser, version), values in self._map.items():
      if key is None:
        continue
      index = (total_metric_name, None, browser, version)
      total_metric_name = f'{metric}_Total'
      self._map.setdefault(index, [])
      total_values = self._map.get(index)
      assert total_values is not None
      total_values.extend(values)

  def write_csv(self, output_file: str, append: bool):
    self.calc_total_metrics()
    mode = 'a' if append else 'w'
    with open(output_file, mode, newline='', encoding='utf-8') as result_file:
      result_writer = csv.writer(result_file,
                                 delimiter=',',
                                 quotechar='"',
                                 quoting=csv.QUOTE_NONNUMERIC)
      if not append:
        result_writer.writerow(['metric', 'browser', 'version'] +
                              ['avg', 'stdev', 'stdev%', '', 'raw_values..'])
      for (metric, key, browser, version), values in self._map.items():
        metric_str = metric + '_' + key if key is not None else metric
        error = self._error.get((metric, key, browser, version))
        avg = statistics.fmean(values)
        if error is None:
          stdev = statistics.stdev(values) if len(values) > 1 else 0
        else:
          stdev = error
        rstdev = stdev / avg if avg > 0 else 0
        result_writer.writerow([metric_str, browser, version] +
                                [avg, stdev, rstdev] + [''] + values)
    self._map = {}
    self._error = {}
