from . import DocumentType
from . import Document
from .. import Constants
from typing import Optional, Collection
from papis.arxiv import find_arxivid_in_text, validate_arxivid
from papis.arxiv import Importer as ImportArxiv

class Arxiv(DocumentType):

    @classmethod
    def validate(cls: Arxiv, doc_id: str) -> Optional[str]:
        """{{{
        Gets ArXiv ID from passed string and attempts to validate it

        :param doc_id: The string from which to extract ArXiv ID

        {{{
        >>> Arxiv.validate('arXiv:1010.4840v2')
        '1010.4840v2'
        >>> Arxiv.validate('hi there') is None
        True

        }}}
        }}}"""
        found_arxiv_id = find_arxivid_in_text(doc_id) or doc_id
        try:
            validate_arxivid(found_arxiv_id)
            return found_arxiv_id
        except:
            return None

    @classmethod
    def download(cls: Arxiv, doc: Document, outdir=Constants.DOWNLOAD_DIR, **kwargs) -> Collection[str]:
        paper_importer = ImportArxiv(doc.doc_id)
        paper_importer.fetch()
        # paper_doi = paper_importer.ctx.data.get('doi')
        doc.update(paper_importer.ctx.data)
        # document.files = 
