__title__ = "wenum"
__version__ = "0.1"

import logging
import sys
import urllib3
from bs4 import MarkupResemblesLocatorWarning

import warnings

#TODO Refactor this file
logger = logging.getLogger("debug_log")
logger.addHandler(logging.NullHandler())
logger.propagate = False

# Will throw warnings when a proxy is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Will throw warnings when the response is very short and has some key chars in it that make BS4 think its a filename
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


# define warnings format
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return " %s:%s: %s:%s\n" % (filename, lineno, category.__name__, message)


warnings.formatwarning = warning_on_one_line


try:
    import pycurl

    if "openssl".lower() not in pycurl.version.lower():
        warnings.warn(
            "Pycurl is not compiled against Openssl. wenum might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information."
        )

    if not hasattr(pycurl, "CONNECT_TO"):
        warnings.warn(
            "Pycurl and/or libcurl version is old. CONNECT_TO option is missing. wenum --ip option will not be available."
        )

except ImportError:
    warnings.warn(
        "fuzz needs pycurl to run. Pycurl could be installed using the following command: $ pip install pycurl"
    )

    sys.exit(1)

from .runtime_session import FuzzSession
