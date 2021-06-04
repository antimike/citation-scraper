import doi
import wikitextparser as wikiparse
from .url import arxiv_url_regex

def get_wiki_lines(wt, predicate=None):
    """get_wiki_lines.
    Splits a WikiText object into a list of lines.

    :param wt: WikiText object
    :param predicate: Boolean function applied as a filter to the returned lines
    """
    return [line for line in wt.contents.split('\n') if not callable(predicate) or predicate(line)]

def get_dois(wt):
    """get_dois.
    Parses DOIs from a WikiText object.

    :param wt: WikiText object
    """
    lines = get_wiki_lines(wt, predicate=any)
    return [doi.find_doi_in_text(l) for l in lines]

def get_arxivs(wt):
    """get_arxivs.
    Uses regex matching to extract ArXiv IDs from a WikiText object.

    :param wt: WikiText object
    """
    lines = get_wiki_lines(wt, predicate=any)
    return [arxiv_url_regex.matches(l).group(1) for l in lines]

