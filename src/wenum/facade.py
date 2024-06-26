from .helpers.file_func import get_home, get_path, get_config_dir
from .helpers.obj_factory import Singleton
from . import __version__ as version
from .externals.moduleman.registrant import MulRegistrant
from .externals.moduleman.loader import DirLoader
from .externals.settings.settings import SettingsBase
from .exception import FuzzExceptNoPluginError, FuzzExceptPluginLoadError

import os


ERROR_CODE = -1


class Settings(SettingsBase):
    def get_config_file(self):
        config_file = "wenum-config.toml"

        config = os.path.join(get_config_dir(check=False), config_file)
        legacy_config = os.path.join(get_home(check=False), config_file)

        if os.path.exists(config):
            return config
        elif os.path.exists(legacy_config):
            return legacy_config
        return os.path.join(get_config_dir(check=True), config_file)

    def set_defaults(self):
        """Creating a default config"""
        return dict(
            plugins=[("bing_apikey", ""), ("shodan_apikey", "")],
            kbase=[
                (
                    "discovery.blacklist",
                    ".svg-.css-.js-.jpg-.gif-.png-.jpeg-.mov-.avi-.flv-.ico",
                )
            ],
            connection=[
                ("conn_delay", "90"),
                ("req_delay", "90"),
                ("retries", "3"),
                ("User-Agent", "wenum/%s" % version),
            ],
            general=[
                ("default_printer", "json"),
                ("cancel_on_plugin_except", "0"),
                ("concurrent_plugins", "3"),
                ("lookup_dirs", "."),
                ("encode_space", "1"),
            ],
        )


class MyRegistrant(MulRegistrant):
    def get_plugin(self, identifier):
        try:
            return MulRegistrant.get_plugin(self, identifier)
        except KeyError as e:
            raise FuzzExceptNoPluginError(
                "Requested plugin %s. Error: %s" % (identifier, str(e))
            )


class Facade(metaclass=Singleton):
    def __init__(self):

        self.__plugins = dict(
            printers=None, scripts=None, encoders=None, iterators=None, payloads=None,
        )

        self.settings: Settings = Settings()

    def _load(self, cat):
        try:
            if cat not in self.__plugins:
                raise FuzzExceptNoPluginError("Non-existent plugin category %s" % cat)

            if not self.__plugins[cat]:
                loader_list = []
                loader_list.append(
                    DirLoader(**{"base_dir": cat, "base_path": get_path("../plugins")})
                )
                loader_list.append(
                    DirLoader(**{"base_dir": cat, "base_path": get_home()})
                )
                self.__plugins[cat] = MyRegistrant(loader_list)

            return self.__plugins[cat]
        except Exception as e:
            raise FuzzExceptPluginLoadError("Error loading plugins: %s" % str(e))

    def proxy(self, which):
        return self._load(which)

    def get_registrants(self):
        return self.__plugins.keys()

    def __getattr__(self, name):
        if name in ["printers", "payloads", "iterators", "encoders", "scripts"]:
            return self._load(name)
        else:
            raise AttributeError
