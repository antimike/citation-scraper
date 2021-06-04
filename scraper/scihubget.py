#!/bin/python3

from scidownl import *
import sys

out = 'paper'
for doi in sys.argv:
    SciHub(doi, out).download()
