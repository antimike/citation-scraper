"""Module for working with ArXiv documents
For local development:

>>> import sys
>>> sys.path.append('/home/user/Source/citation-scraper')
"""

from __future__ import annotations
from typing import Optional, Collection
from papis.arxiv import find_arxivid_in_text, validate_arxivid
from papis.arxiv import Importer as ImportArxiv
from papis.arxiv import Downloader as DownloadArxiv
from scraper.base_classes.document import Document, DocumentType
from scraper import Constants


class Arxiv(DocumentType):
    """class Arxiv
    DocumentType subclass to represent documents defined via an ArXiv ID
    """

    @classmethod
    def validate(cls: Arxiv, doc_id: str) -> Optional[str]:
        """
        Gets ArXiv ID from passed string and attempts to validate it

        :param doc_id: The string from which to extract ArXiv ID

        >>> Arxiv.validate('arXiv:1010.4840v2')
        '1010.4840v2'
        >>> Arxiv.validate('hi there') is None
        True
        """
        found_arxiv_id = find_arxivid_in_text(doc_id) or doc_id
        try:
            validate_arxivid(found_arxiv_id)
            return found_arxiv_id
        except:
            return None

    @classmethod
    def download(
        cls: Arxiv, doc: Document, outdir=Constants.DOWNLOAD_DIR, **kwargs
    ) -> Collection[str]:
        """
        >>> arxiv_id = '1701.00660'
        >>> doc = Document(arxiv_id)
        """
        downloader = DownloadArxiv.match(doc.doc_id)
        if downloader is None:
            raise TypeError('This document does not appear to be associated with a properly-formatted Arxiv ID')
        importer = ImportArxiv(downloader.arxivid)
        importer.fetch()
        doc.update(importer.ctx.data)
