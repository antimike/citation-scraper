import wikitextparser as wikiparse
import sys, os
sys.path.append("{}/regex-dict".format(os.environ["REGEX_DICT_ROOT"]))
import RegexDict

def get_wiki_sections(page):
    """get_wiki_sections.
    Parses a WikiText page into sections.

    :param page: Page object to parse
    """
    return RegexDict(
        {t.lower().strip(): s for s in wikiparse.parse(page).sections if (t := s.title) is not None}
    )
