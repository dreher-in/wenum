from __future__ import annotations
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wenum.facade import Facade

from urllib.parse import ParseResult, urlparse, parse_qs

from wenum.exception import FuzzExceptBadAPI


class FuzzRequestParse(ParseResult):
    @property
    def ffname(self):
        """
        Returns script plus extension from an URL. ie. http://www.localhost.com/kk/index.html?id=3
        will return index.html
        """
        u = self.path.split("/")[-1:][0]

        return u

    @property
    def fext(self):
        """
        Returns script extension from an URL. ie. http://www.localhost.com/kk/index.html?id=3
        will return .html
        """
        return os.path.splitext(self.ffname)[1]

    @property
    def fname(self):
        """
        Returns script name from an URL. ie. http://www.localhost.com/kk/index.html?id=3
        will return index
        """
        return os.path.splitext(self.ffname)[0]

    @property
    def isbllist(self):
        fext = self.fext
        return fext != "." and fext in Facade().settings.get(
            "kbase", "discovery.blacklist"
        ).split("-")

    def cache_key(self, base_urlp=None):
        scheme = self.scheme
        netloc = self.netloc

        if base_urlp:
            scheme = self.scheme if self.scheme else base_urlp.scheme
            netloc = self.netloc if self.netloc else base_urlp.netloc

        key = "{}-{}-{}-{}".format(scheme, netloc, self.path, self.params)
        dicc = {"g{}".format(key): True for key in parse_qs(self.query).keys()}

        # take URL parameters into consideration
        url_params = list(dicc.keys())
        url_params.sort()
        key += "-" + "-".join(url_params)

        return key


def parse_url(url):
    # >>> urlparse.urlparse("http://some.page.pl/nothing.py;someparam=some;otherparam=other?query1=val1&query2=val2#frag")
    # ParseResult(scheme='http', netloc='some.page.pl', path='/nothing.py', params='someparam=some;otherparam=other', query='query1=val1&query2=val2', fragment='frag')

    scheme, netloc, path, params, query, fragment = urlparse(url)
    return FuzzRequestParse(scheme, netloc, path, params, query, fragment)


def check_content_type(fuzz_result, which):
    ctype = None
    if "Content-Type" in fuzz_result.history.headers.response:
        ctype = fuzz_result.history.headers.response["Content-Type"]

    if which == "text":
        return not ctype or (
            ctype and any([ctype.find(x) >= 0 for x in ["text/plain"]])
        )
    else:
        raise FuzzExceptBadAPI("Unknown content type")
