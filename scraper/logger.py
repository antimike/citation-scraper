import logging
import json
from functools import wraps
import os

logging.basicConfig(filename='{}/get-crossref-data.log'.format(os.environ['PYTHON_REPO']), encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

def log_and_return(fn):
    """log_and_return.
    Decorator and miniature IOC container.
    Wraps the passed function with a generator which processes return values and exceptions.

    :param fn: wrapped (decorated) function
    """
    @wraps(fn)
    def wrapper(callback, *args, **kwargs):
        while True:
            try:
                yield callback(fn(*args, **kwargs))
            except Exception as e:
                yield callback(e)
    return wrapper

def write_json_to_file(data, outfile):
    """write_json_to_file.
    Writes a JSON dump of the passed data to the specified file, or returns to stdout if outfile is None

    :param data: Data to dump to JSON
    :param outfile: File to write.  Uses stdout if None

    >>> print(write_json_to_file({'string': 'example', 'key': ['value1', 'value2': , 'value3']}, None))
    {
        "key": [
            "value1",
            "value2",
            "value3"
        ],
        "string": "example"
    }
    """
    formatted = json.dumps(data, indent=4, sort_keys=True)
    if outfile is None:
        return formatted
    else:
        with open(outfile, 'w') as f:
            f.write(formatted)
        return ''

