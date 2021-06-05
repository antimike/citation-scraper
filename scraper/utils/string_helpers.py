import time, re
import pdftitle
import logging
from ..parsing import validate_and_parse_url

logger = logging.getLogger()

def get_wiki_page_id(string):
    """get_wiki_page_id.
    Gets a Wikipedia 'page ID' from the article's URL.
    If the passed URL is invalid, simply returns the original string.

    :param string: String to interpret as either a URL or search term
    """
    try:
        parsed = validate_and_parse_url(string)
        if 'wiki' not in parsed.netloc.lower():
            raise ValueError("The URL {} does not appear to belong to a Wikipedia article".format(string))
        ret = parsed.path.split(r'/')[-1]
    except ValueError:
        ret = string
    return ret

def get_datetime_string(format_string='%m:%d:%Y:%X'):
    """
    Returns a string representation of current (local) time

    :kw format_string: Format string to pass to strftime (optional)
    """
    return time.strftime(format_string, time.localtime())

def sanitize_filename(name, extension='pdf', replacement_char='_', **kwargs):
    """
    Removes whitespace and replaces with '_'.  Also ensures proper extension is appended.

    :param name: Name to sanitize
    :param kwargs: Dict of characters to replace; e.g., {':': '%'} will replace all occurrences of ':' with '%'.  Dict items will be passed to re.sub(), and so should be properly escaped.

    {{{
    >>> sanitize_filename('Linear Algebra and its Applications')
    'Linear_Algebra_and_its_Applications.pdf'

    }}}
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    name = name.rstrip().lstrip().removesuffix(extension)
    name = clean_string(name, default_replacement=replacement_char, **kwargs)
    return name + extension

def clean_string(string, default_replacement='_', replacements={}, **kwargs):
    if string is None:
        return None
    patterns_to_replace = {
        r'\s+', ':', r'\\', r'\/', r"\$", r'%', r'#', r'@', r'!', r'\*', r'\(', r'\)', r'\[', r'\]', r'\{', r'\}', r'\?', r'\+', r'\<', r'\>', r'\.'
    }
    replacements = {
        p: default_replacement for p in patterns_to_replace
    } | kwargs
    for p, r in replacements.items():
        string = re.sub(p, r, string)
    return string

def get_title_as_filename(file_id, extension='pdf', **kwargs):
    """
    Attempts to create a filename out of the title of the PDF.  Uses f'paper_{datetime}.pdf' as a fallback in case this fails.  If a valid path is not provided, simply returns a sanitized version of the passed string.

    :param pdf: File pointer, path, or string to format as a path
    :param extension: (Optional) Extension to append to filename (default = 'pdf')
    :param kwargs: Dictionary of characters to replace during path sanitation.  See `sanitize_filename` for details.

    {{{
    >>> fname = '/home/user/.dotfiles/tag-library/cvetkovic/paper.pdf'
    >>> get_title_as_filename(fname)
    'Linear_Algebra_and_its_Applications.pdf'
    >>> with open(fname, 'rb') as fptr:
    ...     name = get_title_as_filename(fptr)
    >>> name
    'Linear_Algebra_and_its_Applications.pdf'
    >>> get_title_as_filename('hi there')
    'hi_there.pdf'

    }}}
    """
    try:
        name = pdftitle.get_title_from_file(file_id)
    except TypeError:
        name = pdftitle.get_title_from_io(file_id)
    except FileNotFoundError:
        return sanitize_filename(file_id)
    except Exception as e:
        logger.warning('Failed to get title of PDF file "%s".  Exception: %s', file_id[:100], e)
        name = f'paper_{get_datetime_string()}.pdf'
    return sanitize_filename(name, extension=extension)
