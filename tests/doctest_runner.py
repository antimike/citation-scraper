import sys, os
sys.path.append("{}/scraper".format(os.environ["CITATION_SCRAPER_ROOT"]))
import scraper

if __name__ == "main":
    import doctest
    # doctest.test_mod(scraper.parsing)
