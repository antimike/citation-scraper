"""Module for working with documents identified by a DOI"""

from __future__ import annotations
import doi
import glob
from scidownl import scidownl
from typing import Optional, Collection
from scraper import Constants
from scraper.base_classes.document import Document, DocumentType


class Doi(DocumentType):
    @classmethod
    def validate(cls: Doi, doc_id: str) -> Optional[str]:
        """{{{
        Gets DOI from a doc_id

        :param doc_id: doc_id to extract DOI from (probably the DOI itself or a URL)

        {{{
        >>> arg = 'http://dx.doi.org/10.1016/j.entcs.2012.08.017'
        >>> get_validated_doi(arg)
        '10.1016/j.entcs.2012.08.017'
        >>> doi.validate_doi('10.1016/j.entcs.2012.08.017')
        'https://linkinghub.elsevier.com/retrieve/pii/S1571066112000473'

        }}}
        }}}"""
        ret = doi.find_doi_in_text(doc_id)
        try:
            doi.validate_doi(ret)
            return ret
        except ValueError:
            return None

    @classmethod
    def download(
        cls: Doi, doc_id: str, outdir=Constants.DOWNLOAD_DIR, **kwargs
    ) -> Collection[str]:
        """{{{
        Downloads paper with given DOI to specified directory

        :param doc_id: DOI of paper to download

        {{{
        >>> doc_id = '10.1016/j.entcs.2012.08.017'
        >>> DOWNL = '/home/user/Downloads/test'
        >>> download_paper(doc_id, outdir=DOWNL)
        [INFO] Choose the available link 1: http://sci-hub.se
        [INFO] PDF url ->
                http://moscow.sci-hub.se/2475/0a73dc6d1cf609644f4
        2dd1a2fd80f85/manzyuk2012.pdf
        [INFO] Article title ->
                A Simply Typed λ-Calculus of Forward Automatic Di
        fferentiation
        [INFO] Verifying...
        [INFO] Verification success.
        [100%] Progress: 284881 / 284881
        [INFO] Done.

        }}}
        }}}"""
        scidownl.SciHub(doc_id, outdir).download(1)
        return glob.glob(f"{outdir}/*.pdf")

    @classmethod
    def run(cls: Doi, doc: Document) -> None:
        doc.download().get_info().add_to_library()
