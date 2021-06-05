"""Module for working with documents identified by download URL"""

import scihub
from operator import itemgetter
from scraper.base_classes.document import Document, DocumentType
from scraper import Constants
from scraper.utils import sanitize_filename, get_title_as_filename
from typing import Optional, Collection
from urllib.parse import urlsplit, urlunsplit, SplitResult
from validators import url as valid_total_url


class UrlDoc(DocumentType):
    @classmethod
    def validate(cls: DocumentType, doc_id: str) -> Optional[str]:
        """{{{
        Parses and validates a doc_id as a URL

        :param doc_id: doc_id input to parse and validate

        {{{
        >>> url = 'https://www.google.com'
        >>> get_validated_url(url)
        'https://www.google.com'
        >>> url = 'http://www.cs.ox.ac.uk/people/jamie.vicary/IntroductionToCategoricalQuantumMechanics.pdf'
        >>> get_validated_url(url)
        'https://www.cs.ox.ac.uk/people/jamie.vicary/IntroductionToCategoricalQuantumMechanics.pdf'

        }}}
        }}}"""
        defaults = {
            "scheme": "https",
            "netloc": None,
            "path": None,
            "query": None,
            "fragment": None,
        }
        split_url = {
            k: (defaults.get(k) or v) for k, v in urlsplit(doc_id)._asdict().items()
        }
        url = urlunsplit(SplitResult(**split_url))
        try:
            valid_total_url(url)
            return url
        except:
            return None

    @classmethod
    def download(
        cls: DocumentType,
        doc_id: str,
        outdir=Constants.DOWNLOAD_DIR,
        fname=None,
        **kwargs,
    ) -> Collection[str]:
        """{{{
        Downloads paper based on URL, Arxiv ID, or DOI

        :param doc_id: URL of PDF to download
        :param outdir: Directory to download to.  If none is provided, '/home/user/Downloads' will be used
        :param fname: Name of downloaded file.  If none is provided, `get_title_as_filename` will be used to infer a filename

        {{{
        >>> url = "http://www.cs.ox.ac.uk/people/jamie.vicary/IntroductionToCategoricalQuantumMechanics.pdf"
        >>> download_paper_generic(url)
        '/home/user/Downloads/paper_05_31_2021_17_10_44.pdf'

        }}}
        }}}"""
        pdf, url = itemgetter("pdf", "url")(scihub.SciHub().fetch(doc_id))
        fname = sanitize_filename(fname) or get_title_as_filename(pdf)
        path = f"{outdir}/{fname}"
        with open(path, "xb") as fptr:
            fptr.write(pdf)
        return path
