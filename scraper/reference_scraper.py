#!/bin/env python3
import sys

args = sys.argv
try:
    url = args[1]
except IndexError:
    raise ValueError("No URL was passed")
outfile = args[2] if len(args) > 2 else None
# if not valid_url(url):
    # raise ValueError("The passed URL was improperly formatted")
# else:
    # scrape_url_for_refs(url, outfile=outfile)

