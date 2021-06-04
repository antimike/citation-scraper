import urllib
import requests
import re

arxiv_url_regex = re.compile(r'arxiv\.org\/([^\s\.]+)[\.]?[\s|$]+')
arxiv_link_regex = re.compile(r'arxiv:([^\s\.]+)[\.\)\[]?')

def validate_and_parse_url(string):
    """validate_and_parse_url.
    Convenience wrapper around urllib.parse.urlsplit that raises an exception if the URL can't be parsed

    :param string: URL to parse

    >>> validate_and_parse_url("https://en.wikipedia.org/wiki/Double_copy_theory")
    SplitResult(scheme='https', netloc='en.wikipedia.org', path='/wiki/Double_copy_theory', query='', fragment='')
    >>> validate_and_parse_url("fake")
    Traceback (most recent call last):
      ...
    ValueError: The string 'fake' does not appear to be a URL
    """
    parsed = urllib.parse.urlsplit(urllib.parse.unquote(string))
    if not all([parsed.scheme, parsed.netloc, parsed.path]):
        raise ValueError("The string '{}' does not appear to be a URL".format(string))
    return parsed

def valid_url(url):
    """valid_url.
    Pings the passed URL to validate its existence.

    :param url: URL to ping

    >>> valid_url("https://en.wikipedia.org/wiki/Double_copy_theory")
    True
    >>> valid_url("fake")
    False
    """
    try:
        ping = requests.head(url)
        return ping.status_code < 400
    except Exception:
        return False

def get_wiki_page_id(string):
    """get_wiki_page_id.
    Gets a Wikipedia 'page ID' from the article's URL.
    If the passed URL is invalid, simply returns the original string.

    :param string: String to interpret as either a URL or search term

    >>> get_wiki_page_id('Bivector')
    'Bivector'
    >>> get_wiki_page_id('https://en.wikipedia.org/wiki/Double_copy_theory')
    'Double_copy_theory'
    """
    try:
        parsed = validate_and_parse_url(string)
        if 'wiki' not in parsed.netloc.lower():
            raise ValueError("The URL {} does not appear to belong to a Wikipedia article".format(string))
        ret = parsed.path.split(r'/')[-1]
    except ValueError:
        ret = string
    return ret

def get_arxiv_id_from_url(url):
    """get_arxiv_id_from_url.
    Gets the URL-decoded ArXiv ID from a URL
    Returns None if no ArXiv ID is found

    :param url: URL to parse

    >>> get_arxiv_id_from_url('http://arxiv.org/abs/1004.0476')
    '1004.0476'
    >>> get_arxiv_id_from_url('http://edwardbetts.com/find_link?q=Double_copy_theory') is None
    True
    >>> get_arxiv_id_from_url('fake')
    Traceback (most recent call last):
      ...
    ValueError: The string 'fake' does not appear to be a URL
    """
    parsed = validate_and_parse_url(url)
    if 'arxiv' not in parsed.netloc.lower():
        return None
    return r'/'.join(
        [s for s in parsed.path.split(r'/') if not s == 'abs']
    ).strip(r'/')
