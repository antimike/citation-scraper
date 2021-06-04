
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


# Validator = Callable[str, Optional[str]]
# Downloader = Callable[[str, ...], Collection[str]]
# Scraper = Callable[dict, dict]

class _DocumentType(ABC):

    @classmethod
    @abstractmethod
    def validate(cls: _DocumentType, doc_id: str) -> Optional[str]: ...

    @classmethod
    @abstractmethod
    def download(cls: _DocumentType, document: Document, outdir=DOWNLOAD_DIR, **kwargs) -> Collection[str]: ...

    @classmethod
    def run(cls: _DocumentType, doc: Document) -> None:
        """
        Runs the main Document methods in the correct order for the document type
        """
        doc.download().get_info().add_to_library()

    @classmethod
    def scrape(cls: _DocumentType, document: Document) -> dict:
        """
        Combines data from Papis's Crossref search with the full Crossref API, in a way that respects Papis's naming conventions
        """
        document.info |= cls._consolidate_doi_data(
            cls._get_papis_data_from_doi(document.info.get('doi')),
            cls._get_crossref_data_from_doi(document.info.get('doi'))
        )

    @classmethod
    def _consolidate_doi_data(cls, papis_data, cref_data):
        """{{{
        Merges data obtained from Crossref and internally processed by Papis with that obtained directly from the Crossref API

        {{{
        >>> doc_id = '10.1016/j.entcs.2012.08.017'
        >>> papis_data = get_papis_data_from_doi(doc_id)
        >>> cref_data = get_crossref_data_from_doi(doc_id)
        >>> consolidate_doi_data(papis_data, cref_data)
        {'indexed': {'date-parts': [[2020, 4, 17]],
          'date-time': '2020-04-17T11:03:30Z',
          'timestamp': 1587121410174},
         'reference-count': 13,
         'license': [{'URL': 'https://www.elsevier.com/td
        m/userlicense/1.0/',
           'start': {'date-parts': [[2012, 9, 1]],
            'date-time': '2012-09-01T00:00:00Z',
            'timestamp': 1346457600000},
           'delay-in-days': 0,
           'content-version': 'tdm'},
          {'URL': 'http://creativecommons.org/licenses/by
        -nc-nd/3.0/',
           'start': {'date-parts': [[2013, 7, 29]],
            'date-time': '2013-07-29T00:00:00Z',
            'timestamp': 1375056000000},
           'delay-in-days': 331,
           'content-version': 'vor'}],
         'content-domain': {'domain': [], 'crossmark-rest
        riction': False},
         'short-container-title': ['Electronic Notes in T
        heoretical Computer Science'],
         'published-print': {'date-parts': [[2012, 9]]},
         'created': {'date-parts': [[2012, 9, 28]],
          'date-time': '2012-09-28T00:13:22Z',
          'timestamp': 1348791202000},
         'page': '257-272',
         'source': 'Crossref',
         'is-referenced-by-count': 6,
         'prefix': '10.1016',
         'member': '78',
         'reference': [{'key': '10.1016/j.entcs.2012.08.0
        17_br0010',
           'unstructured': 'Blute, R., T. Ehrhard and C.
        Tasson, A convenient differential category, Cahie
        r de Topologie et Géométrie Différentielle Catégo
        riques (2011), to appear. URL http://arxiv.org/ab
        s/1006.3140.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0020',
           'first-page': '622',
           'article-title': 'Cartesian differential categ
        ories',
           'volume': '22',
           'author': 'Blute',
           'year': '2009',
           'journal-title': 'Theory Appl. Categ.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0030',
           'doi-asserted-by': 'crossref',
           'first-page': '213',
           'DOI': '10.1016/j.entcs.2010.08.013',
           'article-title': 'Categorical models for simpl
        y typed resource calculi',
           'volume': '265',
           'author': 'Bucciarelli',
           'year': '2010',
           'journal-title': 'Electron. Notes Theor. Compu
        t. Sci.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0040',
           'doi-asserted-by': 'crossref',
           'first-page': '1',
           'DOI': '10.1016/S0304-3975(03)00392-X',
           'article-title': 'The differential lambda-calc
        ulus',
           'volume': '309',
           'author': 'Ehrhard',
           'year': '2003',
           'journal-title': 'Theoret. Comput. Sci.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0050',
           'author': 'Eilenberg',
           'first-page': '421',
           'year': '1966',
           'article-title': 'Closed categories',
           'series-title': 'Proc. Conf. Categorical Algeb
        ra'},
          {'key': '10.1016/j.entcs.2012.08.017_br0060',
           'author': 'Griewank',
           'volume': 'vol. 19',
           'year': '2000',
           'article-title': 'Evaluating derivatives'},
          {'key': '10.1016/j.entcs.2012.08.017_br0070',
           'doi-asserted-by': 'crossref',
           'first-page': '1',
           'DOI': '10.1007/BF01220868',
           'article-title': 'Monads on symmetric monoidal
         closed categories',
           'volume': '21',
           'author': 'Kock',
           'year': '1970',
           'journal-title': 'Arch. Math. (Basel)'},
          {'key': '10.1016/j.entcs.2012.08.017_br0080',
           'doi-asserted-by': 'crossref',
           'first-page': '113',
           'DOI': '10.1007/BF01304852',
           'article-title': 'Strong functors and monoidal
         monads',
           'volume': '23',
           'author': 'Kock',
           'year': '1972',
           'journal-title': 'Arch. Math. (Basel)'},
          {'key': '10.1016/j.entcs.2012.08.017_br0090', '
        author': 'Manzyuk'},
          {'key': '10.1016/j.entcs.2012.08.017_br0100',
           'doi-asserted-by': 'crossref',
           'first-page': '55',
           'DOI': '10.1016/0890-5401(91)90052-4',
           'article-title': 'Notions of computation and m
        onads',
           'volume': '93',
           'author': 'Moggi',
           'year': '1991',
           'journal-title': 'Inform. and Comput.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0110',
           'doi-asserted-by': 'crossref',
           'first-page': '1',
           'DOI': '10.1145/1330017.1330018',
           'article-title': 'Reverse-mode AD in a functio
        nal framework: Lambda the ultimate backpropagator
        ',
           'volume': '30',
           'author': 'Pearlmutter',
           'year': '2008',
           'journal-title': 'ACM Trans. Program. Lang. Sy
        st.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0120',
           'doi-asserted-by': 'crossref',
           'first-page': '361',
           'DOI': '10.1007/s10990-008-9037-1',
           'article-title': 'Nesting forward-mode AD in a
         functional framework',
           'volume': '21',
           'author': 'Siskind',
           'year': '2008',
           'journal-title': 'Higher Order Symbol. Comput.
        '},
          {'key': '10.1016/j.entcs.2012.08.017_br0130',
           'unstructured': 'Siskind, J.M. and B.A. Pearlm
        utter, Using polyvariant union-free flow analysis
         to compile a higher-order functional-programming
         language with a first-class derivative operator
        to efficient Fortran-like code, Technical Report
        TR-ECE-08-01, School of Electrical and Computer E
        ngineering, Purdue University, West Lafayette, IN
        , USA (2008). URL http://docs.lib.purdue.edu/ecet
        r/367.'}],
         'container-title': ['Electronic Notes in Theoret
        ical Computer Science'],
         'original-title': [],
         'link': [{'URL': 'https://api.elsevier.com/conte
        nt/article/PII:S1571066112000473?httpAccept=text/
        xml',
           'content-type': 'text/xml',
           'content-version': 'vor',
           'intended-application': 'text-mining'},
          {'URL': 'https://api.elsevier.com/content/artic
        le/PII:S1571066112000473?httpAccept=text/plain',
           'content-type': 'text/plain',
           'content-version': 'vor',
           'intended-application': 'text-mining'}],
         'deposited': {'date-parts': [[2018, 11, 20]],
          'date-time': '2018-11-20T13:21:41Z',
          'timestamp': 1542720101000},
         'score': 1.0,
         'subtitle': [],
         'short-title': [],
         'issued': {'date-parts': [[2012, 9]]},
         'references-count': 13,
         'alternative-id': ['S1571066112000473'],
         'relation': {'cites': []},
         'ISSN': ['1571-0661'],
         'issn-type': [{'value': '1571-0661', 'type': 'pr
        int'}],
         'doi': '10.1016/j.entcs.2012.08.017',
         'url': 'http://dx.doi.org/10.1016/j.entcs.2012.0
        8.017',
         'author_list': [{'given': 'Oleksandr',
           'family': 'Manzyuk',
           'affiliation': []}],
         'journal': 'Electronic Notes in Theoretical Comp
        uter Science',
         'language': 'en',
         'pages': '257--272',
         'doc_url': 'https://api.elsevier.com/content/art
        icle/PII:S1571066112000473?httpAccept=text/plain'
        ,
         'year': 2012,
         'month': 9,
         'publisher': 'Elsevier BV',
         'citations': [{'unstructured': 'Blute, R., T. Eh
        rhard and C. Tasson, A convenient differential ca
        tegory, Cahier de Topologie et Géométrie Différen
        tielle Catégoriques (2011), to appear. URL http:/
        /arxiv.org/abs/1006.3140.'},
          {'year': '2009',
           'journal-title': 'Theory Appl. Categ.',
           'volume': '22',
           'author': 'Blute',
           'first-page': '622',
           'article-title': 'Cartesian differential categ
        ories'},
          {'year': '2010',
           'journal-title': 'Electron. Notes Theor. Compu
        t. Sci.',
           'article-title': 'Categorical models for simpl
        y typed resource calculi',
           'volume': '265',
           'first-page': '213',
           'doi': '10.1016/j.entcs.2010.08.013',
           'author': 'Bucciarelli'},
          {'year': '2003',
           'journal-title': 'Theoret. Comput. Sci.',
           'article-title': 'The differential lambda-calc
        ulus',
           'volume': '309',
           'first-page': '1',
           'doi': '10.1016/S0304-3975(03)00392-X',
           'author': 'Ehrhard'},
          {'series-title': 'Proc. Conf. Categorical Algeb
        ra',
           'year': '1966',
           'author': 'Eilenberg',
           'first-page': '421',
           'article-title': 'Closed categories'},
          {'year': '2000',
           'article-title': 'Evaluating derivatives',
           'author': 'Griewank',
           'volume': 'vol. 19'},
          {'year': '1970',
           'journal-title': 'Arch. Math. (Basel)',
           'article-title': 'Monads on symmetric monoidal
         closed categories',
           'volume': '21',
           'first-page': '1',
           'doi': '10.1007/BF01220868',
           'author': 'Kock'},
          {'year': '1972',
           'journal-title': 'Arch. Math. (Basel)',
           'article-title': 'Strong functors and monoidal
         monads',
           'volume': '23',
           'first-page': '113',
           'doi': '10.1007/BF01304852',
           'author': 'Kock'},
          {'author': 'Manzyuk'},
          {'year': '1991',
           'journal-title': 'Inform. and Comput.',
           'article-title': 'Notions of computation and m
        onads',
           'volume': '93',
           'first-page': '55',
           'doi': '10.1016/0890-5401(91)90052-4',
           'author': 'Moggi'},
          {'year': '2008',
           'journal-title': 'ACM Trans. Program. Lang. Sy
        st.',
           'article-title': 'Reverse-mode AD in a functio
        nal framework: Lambda the ultimate backpropagator
        ',
           'volume': '30',
           'first-page': '1',
           'doi': '10.1145/1330017.1330018',
           'author': 'Pearlmutter'},
          {'year': '2008',
           'journal-title': 'Higher Order Symbol. Comput.
        ',
           'article-title': 'Nesting forward-mode AD in a
         functional framework',
           'volume': '21',
           'first-page': '361',
           'doi': '10.1007/s10990-008-9037-1',
           'author': 'Siskind'},
          {'unstructured': 'Siskind, J.M. and B.A. Pearlm
        utter, Using polyvariant union-free flow analysis
         to compile a higher-order functional-programming
         language with a first-class derivative operator
        to efficient Fortran-like code, Technical Report
        TR-ECE-08-01, School of Electrical and Computer E
        ngineering, Purdue University, West Lafayette, IN
        , USA (2008). URL http://docs.lib.purdue.edu/ecet
        r/367.'}],
         'title': 'A Simply Typed λ-Calculus of Forward A
        utomatic Differentiation',
         'type': 'article',
         'volume': '286',
         'author': 'Manzyuk, Oleksandr'}

         }}}
        }}}"""
        if papis_data is None or cref_data is None:
            return papis_data or cref_data
        return {
            key: val for key, val in cref_data.items()
            if key not in papis_data
            and key.lower() not in papis_data
        } | papis_data

    @classmethod
    def _get_papis_data_from_doi(cls, doc_id):
        """{{{
        Gets Papis-ified data from Crossref
        This will be both altered and abridged, but unfortunately the full version cannot simply be substituted (Papis will barf)

        {{{
        >>> doc_id = '10.1016/j.entcs.2012.08.017'
        >>> get_papis_data_from_doi(doc_id)
        {'doi': '10.1016/j.entcs.2012.08.017',
         'url': 'http://dx.doi.org/10.1016/j.entcs.2012.08
        .017',
         'author_list': [{'given': 'Oleksandr',
           'family': 'Manzyuk',
           'affiliation': []}],
         'journal': 'Electronic Notes in Theoretical Compu
        ter Science',
         'language': 'en',
         'pages': '257--272',
         'doc_url': 'https://api.elsevier.com/content/arti
        cle/PII:S1571066112000473?httpAccept=text/plain',
         'year': 2012,
         'month': 9,
         'publisher': 'Elsevier BV',
         'citations': [{'unstructured': 'Blute, R., T. Ehr
        hard and C. Tasson, A convenient differential cate
        gory, Cahier de Topologie et Géométrie Différentie
        lle Catégoriques (2011), to appear. URL http://arx
        iv.org/abs/1006.3140.'},
          {'year': '2009',
           'journal-title': 'Theory Appl. Categ.',
           'volume': '22',
           'author': 'Blute',
           'first-page': '622',
           'article-title': 'Cartesian differential catego
        ries'},
          {'year': '2010',
           'journal-title': 'Electron. Notes Theor. Comput
        . Sci.',
           'article-title': 'Categorical models for simply
         typed resource calculi',
           'volume': '265',
           'first-page': '213',
           'doi': '10.1016/j.entcs.2010.08.013',
           'author': 'Bucciarelli'},
          {'year': '2003',
           'journal-title': 'Theoret. Comput. Sci.',
           'article-title': 'The differential lambda-calcu
        lus',
           'volume': '309',
           'first-page': '1',
           'doi': '10.1016/S0304-3975(03)00392-X',
           'author': 'Ehrhard'},
          {'series-title': 'Proc. Conf. Categorical Algebr
        a',
           'year': '1966',
           'author': 'Eilenberg',
           'first-page': '421',
           'article-title': 'Closed categories'},
          {'year': '2000',
           'article-title': 'Evaluating derivatives',
           'author': 'Griewank',
           'volume': 'vol. 19'},
          {'year': '1970',
           'journal-title': 'Arch. Math. (Basel)',
           'article-title': 'Monads on symmetric monoidal
        closed categories',
           'volume': '21',
           'first-page': '1',
           'doi': '10.1007/BF01220868',
           'author': 'Kock'},
          {'year': '1972',
           'journal-title': 'Arch. Math. (Basel)',
           'article-title': 'Strong functors and monoidal
        monads',
           'volume': '23',
           'first-page': '113',
           'doi': '10.1007/BF01304852',
           'author': 'Kock'},
          {'author': 'Manzyuk'},
          {'year': '1991',
           'journal-title': 'Inform. and Comput.',
           'article-title': 'Notions of computation and mo
        nads',
           'volume': '93',
           'first-page': '55',
           'doi': '10.1016/0890-5401(91)90052-4',
           'author': 'Moggi'},
          {'year': '2008',
           'journal-title': 'ACM Trans. Program. Lang. Sys
        t.',
           'article-title': 'Reverse-mode AD in a function
        al framework: Lambda the ultimate backpropagator',
           'volume': '30',
           'first-page': '1',
           'doi': '10.1145/1330017.1330018',
           'author': 'Pearlmutter'},
          {'year': '2008',
           'journal-title': 'Higher Order Symbol. Comput.'
        ,
           'article-title': 'Nesting forward-mode AD in a
        functional framework',
           'volume': '21',
           'first-page': '361',
           'doi': '10.1007/s10990-008-9037-1',
           'author': 'Siskind'},
          {'unstructured': 'Siskind, J.M. and B.A. Pearlmu
        tter, Using polyvariant union-free flow analysis t
        o compile a higher-order functional-programming la
        nguage with a first-class derivative operator to e
        fficient Fortran-like code, Technical Report TR-EC
        E-08-01, School of Electrical and Computer Enginee
        ring, Purdue University, West Lafayette, IN, USA (
        2008). URL http://docs.lib.purdue.edu/ecetr/367.'}
        ],
         'title': 'A Simply Typed λ-Calculus of Forward Au
        tomatic Differentiation',
         'type': 'article',
         'volume': '286',
         'author': 'Manzyuk, Oleksandr'}

         }}}
        }}}"""
        try:
            retrieved = Papis.doi_to_data(doc_id)
        except:
            logger.warning('Exception thrown during Crossref lookup of DOI %s', doc_id)
            return None
        return retrieved

    @classmethod
    def _get_crossref_data_from_doi(cls, doc_id):
        """{{{
        Gets full Crossref data for passed DOI (including references)

        {{{
        >>> doc_id = '10.1016/j.entcs.2012.08.017'
        >>> get_crossref_data_from_doi(doc_id)
        {'indexed': {'date-parts': [[2020, 4, 17]],
          'date-time': '2020-04-17T11:03:30Z',
          'timestamp': 1587121410174},
         'reference-count': 13,
         'publisher': 'Elsevier BV',
         'license': [{'URL': 'https://www.elsevier.com/tdm
        /userlicense/1.0/',
           'start': {'date-parts': [[2012, 9, 1]],
            'date-time': '2012-09-01T00:00:00Z',
            'timestamp': 1346457600000},
           'delay-in-days': 0,
           'content-version': 'tdm'},
          {'URL': 'http://creativecommons.org/licenses/by-
        nc-nd/3.0/',
           'start': {'date-parts': [[2013, 7, 29]],
            'date-time': '2013-07-29T00:00:00Z',
            'timestamp': 1375056000000},
           'delay-in-days': 331,
           'content-version': 'vor'}],
         'content-domain': {'domain': [], 'crossmark-restr
        iction': False},
         'short-container-title': ['Electronic Notes in Th
        eoretical Computer Science'],
         'published-print': {'date-parts': [[2012, 9]]},
         'DOI': '10.1016/j.entcs.2012.08.017',
         'type': 'journal-article',
         'created': {'date-parts': [[2012, 9, 28]],
          'date-time': '2012-09-28T00:13:22Z',
          'timestamp': 1348791202000},
         'page': '257-272',
         'source': 'Crossref',
         'is-referenced-by-count': 6,
         'title': ['A Simply Typed λ-Calculus of Forward A
        utomatic Differentiation'],
         'prefix': '10.1016',
         'volume': '286',
         'author': [{'given': 'Oleksandr',
           'family': 'Manzyuk',
           'sequence': 'first',
           'affiliation': []}],
         'member': '78',
         'reference': [{'key': '10.1016/j.entcs.2012.08.01
        7_br0010',
           'unstructured': 'Blute, R., T. Ehrhard and C. T
        asson, A convenient differential category, Cahier
        de Topologie et Géométrie Différentielle Catégoriq
        ues (2011), to appear. URL http://arxiv.org/abs/10
        06.3140.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0020',
           'first-page': '622',
           'article-title': 'Cartesian differential catego
        ries',
           'volume': '22',
           'author': 'Blute',
           'year': '2009',
           'journal-title': 'Theory Appl. Categ.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0030',
           'doi-asserted-by': 'crossref',
           'first-page': '213',
           'DOI': '10.1016/j.entcs.2010.08.013',
           'article-title': 'Categorical models for simply
         typed resource calculi',
           'volume': '265',
           'author': 'Bucciarelli',
           'year': '2010',
           'journal-title': 'Electron. Notes Theor. Comput
        . Sci.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0040',
           'doi-asserted-by': 'crossref',
           'first-page': '1',
           'DOI': '10.1016/S0304-3975(03)00392-X',
           'article-title': 'The differential lambda-calcu
        lus',
           'volume': '309',
           'author': 'Ehrhard',
           'year': '2003',
           'journal-title': 'Theoret. Comput. Sci.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0050',
           'author': 'Eilenberg',
           'first-page': '421',
           'year': '1966',
           'article-title': 'Closed categories',
           'series-title': 'Proc. Conf. Categorical Algebr
        a'},
          {'key': '10.1016/j.entcs.2012.08.017_br0060',
           'author': 'Griewank',
           'volume': 'vol. 19',
           'year': '2000',
           'article-title': 'Evaluating derivatives'},
          {'key': '10.1016/j.entcs.2012.08.017_br0070',
           'doi-asserted-by': 'crossref',
           'first-page': '1',
           'DOI': '10.1007/BF01220868',
           'article-title': 'Monads on symmetric monoidal
        closed categories',
           'volume': '21',
           'author': 'Kock',
           'year': '1970',
           'journal-title': 'Arch. Math. (Basel)'},
          {'key': '10.1016/j.entcs.2012.08.017_br0080',
           'doi-asserted-by': 'crossref',
           'first-page': '113',
           'DOI': '10.1007/BF01304852',
           'article-title': 'Strong functors and monoidal
        monads',
           'volume': '23',
           'author': 'Kock',
           'year': '1972',
           'journal-title': 'Arch. Math. (Basel)'},
          {'key': '10.1016/j.entcs.2012.08.017_br0090', 'a
        uthor': 'Manzyuk'},
          {'key': '10.1016/j.entcs.2012.08.017_br0100',
           'doi-asserted-by': 'crossref',
           'first-page': '55',
           'DOI': '10.1016/0890-5401(91)90052-4',
           'article-title': 'Notions of computation and mo
        nads',
           'volume': '93',
           'author': 'Moggi',
           'year': '1991',
           'journal-title': 'Inform. and Comput.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0110',
           'doi-asserted-by': 'crossref',
           'first-page': '1',
           'DOI': '10.1145/1330017.1330018',
           'article-title': 'Reverse-mode AD in a function
        al framework: Lambda the ultimate backpropagator',
           'volume': '30',
           'author': 'Pearlmutter',
           'year': '2008',
           'journal-title': 'ACM Trans. Program. Lang. Sys
        t.'},
          {'key': '10.1016/j.entcs.2012.08.017_br0120',
           'doi-asserted-by': 'crossref',
           'first-page': '361',
           'DOI': '10.1007/s10990-008-9037-1',
           'article-title': 'Nesting forward-mode AD in a
        functional framework',
           'volume': '21',
           'author': 'Siskind',
           'year': '2008',
           'journal-title': 'Higher Order Symbol. Comput.'
        },
          {'key': '10.1016/j.entcs.2012.08.017_br0130',
           'unstructured': 'Siskind, J.M. and B.A. Pearlmu
        tter, Using polyvariant union-free flow analysis t
        o compile a higher-order functional-programming la
        nguage with a first-class derivative operator to e
        fficient Fortran-like code, Technical Report TR-EC
        E-08-01, School of Electrical and Computer Enginee
        ring, Purdue University, West Lafayette, IN, USA (
        2008). URL http://docs.lib.purdue.edu/ecetr/367.'}
        ],
         'container-title': ['Electronic Notes in Theoreti
        cal Computer Science'],
         'original-title': [],
         'language': 'en',
         'link': [{'URL': 'https://api.elsevier.com/conten
        t/article/PII:S1571066112000473?httpAccept=text/xm
        l',
           'content-type': 'text/xml',
           'content-version': 'vor',
           'intended-application': 'text-mining'},
          {'URL': 'https://api.elsevier.com/content/articl
        e/PII:S1571066112000473?httpAccept=text/plain',
           'content-type': 'text/plain',
           'content-version': 'vor',
           'intended-application': 'text-mining'}],
         'deposited': {'date-parts': [[2018, 11, 20]],
          'date-time': '2018-11-20T13:21:41Z',
          'timestamp': 1542720101000},
         'score': 1.0,
         'subtitle': [],
         'short-title': [],
         'issued': {'date-parts': [[2012, 9]]},
         'references-count': 13,
         'alternative-id': ['S1571066112000473'],
         'URL': 'http://dx.doi.org/10.1016/j.entcs.2012.08
        .017',
         'relation': {'cites': []},
         'ISSN': ['1571-0661'],
         'issn-type': [{'value': '1571-0661', 'type': 'pri
        nt'}]}

        }}}
        }}}"""
        try:
            retrieved = works.doi(doc_id)
        except:
            logger.warning('Exception thrown during Crossref lookup of DOI %s', doc_id)
            return None
        return retrieved

class Arxiv(_DocumentType):

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
    def download(cls: Arxiv, doc: Document, outdir=DOWNLOAD_DIR, **kwargs) -> Collection[str]:
        paper_importer = ImportArxiv(doc_id)
        paper_importer.fetch()
        # paper_doi = paper_importer.ctx.data.get('doi')
        document.update(paper_importer.ctx.data)
        # document.files = 

class Doi(_DocumentType):

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
    def download(cls: Doi, doc_id: str, outdir=DOWNLOAD_DIR, **kwargs) -> Collection[str]:
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
        return glob.glob(f'{outdir}/*.pdf')

    @classmethod
    def run(cls: Arxiv, doc: Document) -> None:
        doc.download().get_info().add_to_library()



class UrlDoc(_DocumentType):

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
        defaults = {'scheme': 'https', 'netloc': None, 'path': None, 'query': None, 'fragment': None}
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
    def download(cls: DocumentType, doc_id: str, outdir=DOWNLOAD_DIR, fname=None, **kwargs) -> Collection[str]:
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
        pdf, url = itemgetter('pdf', 'url')(scihub.SciHub().fetch(doc_id))
        fname = sanitize_filename(fname) or get_title_as_filename(pdf)
        path = f'{outdir}/{fname}'
        with open(path, 'xb') as fptr:
            fptr.write(pdf)
        return path

class TagList:
    """
    Set-based collection of string tags.  Supports iteration and +/- operations.

    Class methods
    =============
    :clean_tag:
        Returns a "cleaned" version of the passed tag (i.e., stripped of whitespace and other problematic characters)

    :_consolidate_tags:
        Returns the set of unique stripped and cleaned tags contained in the passed arguments

    Operators
    =========
    :+, -:
        Support adding and removing tags via set.union and set.difference

    >>> tl = TagList('one', 'two', 'three')
    >>> str(tl)
    'one three two'
    >>> tl2 = TagList(' boopy    shadoopy   ', ['hi there'], {'yo'})
    >>> str(tl2)
    'yo hi there boopy shadoopy'
    >>> str(tl + tl2)
    'three yo two hi there shadoopy one boopy'
    >>> str(tl - 'two')
    'one three'
    >>> str(tl2 - ['boopy', '   shadoopy '])
    'yo hi there'
    >>> str(tl - tl2)
    'one three two'
    >>> for tag in tl:
    ...     print(tag)
    one
    three
    two
    """

    @classmethod
    def clean_tag(cls: TagList, tag: str) -> str:
        """
        Removes whitespace and replaces problematic characters with '-'

        >>> TagList.clean_tag(' #some_tag   ')
        '#some_tag'
        >>> TagList.clean_tag('(another^tag)')
        '\\(another^tag\\)'
        >>> TagList.clean_tag('$bad_tag')
        '-bad_tag'
        """
        tag = tag.strip()
        allowed_chars = {
            r'\?', r'!', r'\>', r'\<', r'\/', r'\\', r'#', r'\+', r'\*', r'@', r':', r'\(', r'\)', r'\[', r'\]'
        }
        kwargs = {c: c for c in allowed_chars}
        return clean_string(tag, default_replacement='-', **kwargs)

    @classmethod
    def _consolidate_tags(cls: TagLIst, tags: Union[str, Iterable[str]]) -> Set[str]:
        """
        Combines tags passed in the form of either
            (1) a whitespace-delimited string or
            (2) an iterable of strings (note that this includes other TagLists)
        into a single set of cleaned tags.

        >>> tlist = ['a', 'b c', 'a f', 'c f g']
        >>> TagList._consolidate_tags(tlist)
        {'a', 'b', 'c', 'f', 'g'}
        >>> TagList._consolidate_tags('hi there')
        {'hi', 'there'}
        """
        try:
            return set(map(cls.clean_tag, tags.split()))
        except AttributeError:
            return set.union(*[cls._consolidate_tags(item) for item in tags])

    def __init__(self, *tagstrings) -> None:
        self._tags = set.union(*map(self.__class__._consolidate_tags, tagstrings))

    def __add__(self, other) -> TagList:
        return self.__class__(self, other)

    def __sub__(self, other):
        return self.__class__(self._tags.difference(self.__class__(other)._tags))

    def __str__(self):
        return ' '.join(self._tags)

    def __iter__(self):
        return iter(self._tags)

class Document:
    """{{{
    Simple class to represent a document to be downloaded and added to a Papis library

    Properties
    ==========
    files: Collection[str]
        Filepaths of downloaded PDFs

    doctype: _DocumentType
        The type of document represented

    doc_id: str
        Validated document ID

    info: dict
        Document metadata collected from Crossref, ArXiv, Papis importers, etc.

    tags: TagList
        Tags to apply when the document is added to Papis

    Methods
    =======
    :update:
        Updates "info" property using dict.update

    :download:
        Downloads associated files according to doctype

    :get_info:
        Gets document info from Crossref and Papis

    :add_to_library:
        Adds to Papis library

    :tag_files:
        Tags associated files in TMSU, hypertag, and supertag virtual filesystems

    {{{
    >>> string = '1006.3140'
    >>> doc = Document(string)
    >>> doc.doctype
    __main__.Arxiv
    >>> doc.doc_id
    '1006.3140'
    >>> doc.tags += ['test', '  hi there    ']; str(doc.tags)
    'test hi there'
    >>> doc.tags -= 'test'; str(doc.tags)
    'hi there'

    }}}
    }}}"""

    @property
    def files(self) -> Collection[str]:
        return self._files

    @property
    def doctype(self) -> str:
        return self._doctype

    @property
    def doc_id(self) -> str:
        return self._id

    @property
    def info(self) -> dict:
        return self._info

    @property
    def tags(self) -> TagList:
        return self._tags

    @tags.setter
    def tags(self, new_tags) -> None:
        self._tags = TagList(new_tags)

    def __init__(self, doc_id: str, *tags, **opts: Mapping[str, Any]):
        self._files = []
        self._info = opts
        self._tags = TagList(tags)
        for doctype in _DocumentType.__subclasses__():
            if (found := doctype.validate(doc_id)):
                self._doctype = doctype
                self._id = found
                break

    def update(self, info_dict: dict) -> None:
        self._info.update(info_dict)
        return self

    def download(self):
        self._files = self.doctype.download(self)
        return self

    def get_info(self):
        self._info = self.doctype.scrape(self)
        return self

    def add_to_library(self, confirm=True, link=False, **kwargs):
        PapisAdd(
            self.files, self.info | {'tags': str(self.tags)} | kwargs, confirm=confirm, link=link
        )
        return self

    def tag_files(self):
        raise NotImplementedError

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
