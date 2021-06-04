import pypandoc

def convert_html_to_markdown(html):
    """convert_html_to_markdown.
    Uses Pandoc to convert a document from HTML to Markdown.

    :param html: Raw markup to be converted
    """
    return pypandoc.convert_text(html, 'markdown', 'html')
