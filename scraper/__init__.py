# import scraper.apis
import scraper.parsing
from enum import Enum

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

class Constants(Enum):
    DOWNLOAD_DIR = '/home/user/Downloads'
