import pywikibot as pywiki
# from scraper.parsing import get_wiki_page_id
import scraper

def get_pywiki_page(string):
    """get_pywiki_page.
    Gets a wiki page using the `pywikibot` wrapper around the Wikipedia API
    Unlike the other libraries, this one is capable of returning raw wikitext

    :param url: URL of article to get

    >>> pywiki_site = pywiki.Site('en', 'wikipedia')
    >>> pywiki_site
    APISite("en", "wikipedia")
    >>> page = pywiki.Page(pywiki_site, 'Bivector')
    >>> page
    Page('Bivector')
    >>> page.exists()
    True
    >>> get_pywiki_page("https://en.wikipedia.org/wiki/Double_copy_theory")
    Page('Double copy theory')
    """
    article_id = scraper.parsing.get_wiki_page_id(string)
    site = pywiki.Site('en', 'wikipedia')
    page = pywiki.Page(site, article_id)
    assert page.exists(), "A page with ID {} doesn't seem to exist".format(article_id)
    return page
