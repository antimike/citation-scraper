#!/usr/bin/env python3

import sys, os
import yaml

files = sys.argv[1:]
tags = []

for file in files:
    with open(file, 'r') as fstream:
        info = yaml.load(fstream, Loader=yaml.FullLoader)
        newtags = info.get('tags') or ''
        tags += newtags.strip().split(' ')

print(' '.join(set(tags)))
