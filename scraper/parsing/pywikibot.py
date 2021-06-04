from ..config import config

class TemplateParser:
    """TemplateParser.
    Helper class to extract useful information from Wiki templates
    All methods are static
    """

    @staticmethod
    def is_citation(t):
        """is_citation_template.
        Predicate: Determines if a template qualifies as a "citation" based on its title

        :param template_title: Title of the template of interest

        >>> is_citation_template('Template:Cite journal')
        True
        >>> is_citation_template('Template:Doi')
        True
        >>> is_citation_template('Template:Physics-stub')
        False
        """
        return (T := TemplateParser.title(t)) in config.get('citation_template_whitelist', []) \
            or 'cite' in T.lower()

    @staticmethod
    def parse_args(t):
        return dict(tuple([None, *arg.split('=', 1)][-2:]) for arg in t[1])

    @staticmethod
    def title(t):
        return t[0].title()
