import refextract

def search_for_refs(string):
    """search_for_refs.
    Searches for references in a variety of forms from a passed string.

    :param string: String to search
    """
    return refextract.extract_references_from_string(string)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
