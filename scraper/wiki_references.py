"""
RESULTS OF TESTING SO FAR:
It seems the most accurate way to get all the DOIs from a Wiki page is:
1. Get the pagedata through the `wiki` module
2. Parse with `wikitextparser`, using its API to get all 'references'
3. Do a simple search for 'doi' in the resulting array
Test script:

>>> url = 'https://en.wikipedia.org/wiki/Julian_Schwinger'
>>> page = wiki.page(get_wiki_page_id(url))
>>> refs = page.references
>>> dois = {d for r in refs if r is not None and (d := doi.find_doi_in_text(r)) is not None}
>>> arxivs = {m.group(1) for r in refs if (m := arxiv_url_regex.match(r)) is not None}
>>> sorted(list(dois))
['10.1.1.6.9407', '10.1007/s00016-007-0326-6', '10.1051/jphyscol', '10.1103/PhysRev.73.416', '10.1103/PhysRev.74.1439', '10.1103/PhysRev.75.651', '10.1103/PhysRev.76.790', '10.1103/PhysRev.82.664', '10.1103/RevModPhys.74.425']
>>> sorted(list(arxivs))
[]
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
