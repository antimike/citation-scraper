import bs4

def get_refs_from_soup(soup):
    """get_refs_from_soup.
    Returns a list of `<cite>` tags from the passed BeautifulSoup object.

    :param soup: BeautifulSoup object (parsed HTML)
    """
    return soup.find_all('cite', recursive=True)
