from configparser import ConfigParser


class Settings(ConfigParser):
    """Models the settings for clocker."""

    def __init__(self):
        super().__init__()
        self.read('config.ini')
