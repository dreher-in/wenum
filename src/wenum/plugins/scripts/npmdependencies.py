import re

from wenum.plugin_api.base import BasePlugin
from wenum.externals.moduleman.plugin import moduleman_plugin


@moduleman_plugin
class NPMDependencies(BasePlugin):
    name = "npm_deps"
    author = ("Xavi Mendez (@xmendez)",)
    version = "0.1"
    summary = "Looks for npm dependencies definition in js code"
    description = (
        "Extracts npm packages by using regex pattern from the HTTP response and prints it",
    )
    category = ["info", "default"]
    priority = 99

    parameters = ()

    REGEX_PATT = re.compile(r'"([^"]+)":"([^"]+)"', re.MULTILINE | re.DOTALL)
    REGEX_DEP = re.compile(
        r"dependencies:\{(.*?)\}", re.MULTILINE | re.DOTALL | re.IGNORECASE
    )
    REGEX_DEV_DEP = re.compile(
        r"devdependencies:\{(.*?)\}", re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    def __init__(self, session):
        BasePlugin.__init__(self, session)
        self.match = None
        self.match_dev = None

    def validate(self, fuzz_result):
        if fuzz_result.history.urlparse.fext != ".js" or fuzz_result.code != 200:
            return False

        self.match = self.REGEX_DEP.search(fuzz_result.history.content)
        self.match_dev = self.REGEX_DEV_DEP.search(fuzz_result.history.content)

        return self.match is not None or self.match_dev is not None

    def process(self, fuzz_result):
        if self.match_dev:
            for name, version in self.REGEX_PATT.findall(self.match_dev.group(1)):
                self.add_information(f"npm dependency: {name}")

        if self.match:
            for name, version in self.REGEX_PATT.findall(self.match.group(1)):
                self.add_information(f"npm dev dependency{name}")
