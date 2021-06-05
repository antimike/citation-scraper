from .. import Constants
from . import Document
from abc import ABC, abstractmethod
from typing import Optional, Collection
from papis import api as Papis
import logging
from crossref.restful import Works

logger = logging.getLogger()
works = Works()

class _DocumentType(ABC):

    @classmethod
    @abstractmethod
    def validate(cls: _DocumentType, doc_id: str) -> Optional[str]: ...

    @classmethod
    @abstractmethod
    def download(cls: _DocumentType, document: Document, outdir=Constants.DOWNLOAD_DIR, **kwargs) -> Collection[str]: ...

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
