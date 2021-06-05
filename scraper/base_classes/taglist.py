from ..utils import clean_string
from typing import Union, Iterable, Set

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
    def _consolidate_tags(cls: TagList, tags: Union[str, Iterable[str]]) -> Set[str]:
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
