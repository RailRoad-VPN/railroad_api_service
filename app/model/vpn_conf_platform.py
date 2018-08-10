from enum import Enum


class VPNConfigurationPlatform(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, text):
        self.sid = sid
        self.text = text

    IOS = (1, 'iOS', 'Apple iPhone and iPad mobile OS')
    ANDROID = (2, 'Android', 'All Android devices OS')
    WINDOWS = (3, 'Windows', 'Windows OS')
    MACOS = (4, 'macOS', 'Apple Mac OS')
