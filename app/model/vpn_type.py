from enum import Enum


class VPNType(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, text, description):
        self.sid = sid
        self.text = text
        self.description = description

    @staticmethod
    def find_by_text(text):
        if VPNType.UNKNOWN.text == text:
            return VPNType.UNKNOWN
        elif VPNType.OPENVPN.text == text:
            return VPNType.OPENVPN
        elif VPNType.IKEV2.text == text:
            return VPNType.IKEV2

    UNKNOWN = (0, 'unknown', 'Unknown, for reports only')
    OPENVPN = (1, 'openvpn', 'Standard OpenVPN server')
    IKEV2 = (2, 'ikev2', 'IPSec w IKEv2')
