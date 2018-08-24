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

    IOS = (1, 'iOS')
    ANDROID = (2, 'Android')
    WINDOWS = (3, 'Windows')
    MACOS = (4, 'macOS')
