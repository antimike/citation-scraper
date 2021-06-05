import doi

def get_validated_doi_from_pdf(fpath):
    return doi.pdf_to_doi(fpath)
