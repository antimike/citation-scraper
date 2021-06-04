import bs4
import requests
import re

def scrape_url_for_refs(url, outfile=None):
    """scrape_url_for_refs.
    Gets a list of hrefs from the passed URL containing DOI or ArXiv IDs

    :param url: URL to scrape for DOIs and ArXiv IDs
    :param outfile: File to write results to.  If none is provided, results are printed to stdout

    >>> sorted(scrape_url_for_refs('https://en.wikipedia.org/wiki/Orchestrated_objective_reduction'))
    ['//arxiv.org/abs/quant-ph/0005025', '//arxiv.org/abs/quant-ph/9907009', '//citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.130.7027', 'https://doi.org/10.1002%2Fglia.440060207', 'https://doi.org/10.1007%2F3-540-36723-3', 'https://doi.org/10.1007%2Fbf02478259', 'https://doi.org/10.1007%2Fs10701-013-9770-0', 'https://doi.org/10.1007%2Fs10701-013-9770-0', 'https://doi.org/10.1007%2Fs10867-009-9148-x', 'https://doi.org/10.1016%2F0022-5193%2882%2990137-0', 'https://doi.org/10.1016%2FS0896-6273%2804%2900043-1', 'https://doi.org/10.1016%2Fj.cell.2006.12.009', 'https://doi.org/10.1016%2Fj.plrev.2012.07.001', 'https://doi.org/10.1016%2Fj.plrev.2013.08.002', 'https://doi.org/10.1016%2Fj.plrev.2013.08.002', 'https://doi.org/10.1016%2Fj.plrev.2013.11.003', 'https://doi.org/10.1016%2Fj.plrev.2013.11.013', 'https://doi.org/10.1016%2Fj.plrev.2013.11.014', 'https://doi.org/10.1017%2Fs0031819100024591', 'https://doi.org/10.1017%2Fs0140525x00080687', 'https://doi.org/10.1038%2F440611a', 'https://doi.org/10.1063%2F1.4752474', 'https://doi.org/10.1073%2Fpnas.0806273106', 'https://doi.org/10.1073%2Fpnas.89.23.11357', 'https://doi.org/10.1073%2Fpnas.96.13.7541', 'https://doi.org/10.1083%2Fjcb.127.6.1965', 'https://doi.org/10.1097%2F00000542-200608000-00024', 'https://doi.org/10.1098%2Frsta.1998.0254', 'https://doi.org/10.1103%2FPhysRevE.61.4194', 'https://doi.org/10.1103%2FPhysRevE.65.061901', 'https://doi.org/10.1103%2FPhysRevE.80.021912', 'https://doi.org/10.1113%2Fjphysiol.1952.sp004764', 'https://doi.org/10.11225%2Fjcss.5.2_95', 'https://doi.org/10.1142%2FS0129065796000300', 'https://doi.org/10.1207%2Fs15516709cog0000_59', 'https://doi.org/10.1207%2Fs15516709cog0000_59', 'https://doi.org/10.1523%2Fjneurosci.14-05-02818.1994', 'https://doi.org/10.1523%2Fjneurosci.14-05-02818.1994', 'https://doi.org/10.3389%2Ffnint.2012.00093']
    """
    page = requests.get(url)
    parsed_page = bs4.BeautifulSoup(page.content, features="lxml")
    links = parsed_page.findAll('a', attrs={'href': re.compile('')})
    doc_links = [href for link in links
                 if 'arxiv' in (href := link.get('href'))
                 or 'doi' in href]
    if outfile is not None:
        with open(outfile, "w+") as fout:
            lines = ['source_url:{}\n'.format(url), *map(lambda l: l + '\n', doc_links)]
            fout.writelines(lines)
    else:
        return doc_links

if __name__ == "__main__":
    import doctest
    doctest.testmod()
