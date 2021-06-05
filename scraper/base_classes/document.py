from papis.commands.add import run as PapisAdd
from . import TagList, DocumentType
from typing import Collection, Mapping, Any

class Document:
    """{{{
    Simple class to represent a document to be downloaded and added to a Papis library

    Properties
    ==========
    files: Collection[str]
        Filepaths of downloaded PDFs

    doctype: DocumentType
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
        for doctype in DocumentType.__subclasses__():
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
