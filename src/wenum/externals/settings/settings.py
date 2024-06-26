from configparser import ConfigParser
import os
import sys


class SettingsBase:
    """
    Contains application settings. uses a ConfigParser
    """

    def __init__(self, save=False):
        self.cparser = ConfigParser()

        self.set_all(self.set_defaults())
        self.filename = os.path.join(
            self._path_to_program_dir(), self.get_config_file()
        )
        self.cparser.read(self.filename)

    # Base members should implement
    # TODO Mark abstract
    def get_config_file(self):
        """Returns the name of the file where the config is saved."""
        raise NotImplementedError

    def set_defaults(self):
        """
        Returns a dictionary with the default settings in the form of
        { \
                Section: [ \
                    ("setting_x", '5'),
                    ...
                    ("setting_y", '5'),
                ],
        ...
        }
        """
        raise NotImplementedError

    def get(self, section, setting):
        value = self.cparser.get(section, setting)
        return value

    def set_all(self, sett):
        self.cparser = ConfigParser()
        for section, settings in sett.items():
            self.cparser.add_section(section)
            for key, value in settings:
                self.cparser.set(section, key, value)

    def _path_to_program_dir(self):
        """
        Returns path to program directory
        """
        path = sys.argv[0]

        if not os.path.isdir(path):
            path = os.path.dirname(path)

        if not path:
            return "."

        return path
