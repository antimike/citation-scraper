
#!/bin/env/python3

from __future__ import annotations
import logging
import sys, os
import glob
import doi
from scidownl import scidownl
import json, yaml
from crossref.restful import Works
import scihub
from papis import api as Papis
from papis.commands.add import run as PapisAdd
from papis.arxiv import Importer as ImportArxiv
from papis.arxiv import find_arxivid_in_text, validate_arxivid
from operator import itemgetter
from enum import Enum, auto
from typing import NamedTuple, Callable, Optional, Collection, Mapping, Any, Iterable, Union
from abc import abstractmethod, ABC
from urllib.parse import urlsplit, urlunsplit, SplitResult
from validators import url as valid_total_url
import pdftitle
import time
import re

works = Works()
DOWNLOAD_DIR = '/home/user/Downloads'
dois = [get_validated_doi(arg) for arg in sys.argv[1:]]
logger = logging.getLogger()

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

def add_paper_from_doi(doc_id, *tags, confirm=True, link=False, **kwargs):
    """
    Fetches and adds a paper to Papis library from DOI

    :param doc_id: DOI of paper to add
    :param *tags: Tags to apply in Papis
    :kw confirm: (Optional) Whether to confirm adding doc (default = True)
    :kw link: (Optional) Whether to create symlink instead of copying PDF (default = False)
    :param **kwargs: Properties to set in document's info.yaml file
    """
    data = get_consolidated_data_from_doi(doc_id) | {
        'tags': ' '.join(tags)
    } | kwargs
    title = data.get('title')
    subdir = get_title_as_filename(title, extension='pdf')
    files = download_paper_from_doi(doc_id, outdir=f'{DOWNLOAD_DIR}/{subdir}')
    PapisAdd(files, data, confirm=confirm, link=link)

# def add_paper_from_url(url, *tags, confirm=True, link=False):
# def download_paper(doc_id):


def get_validated_doi_from_pdf(fpath):
    return doi.pdf_to_doi(fpath)


# from papis.commands.add import run as PapisAdd
"""
# Physics

* stat-mech
    * fermions
        * chandresekhar
"""
