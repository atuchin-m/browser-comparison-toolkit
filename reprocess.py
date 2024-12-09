#!env python3

import components.result_map as result_map

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input', type=str)
parser.add_argument('output', type=str)
args = parser.parse_args()

r = result_map.ResultMap()
r.read_csv(args.input)

r.write_csv(None, args.output)
