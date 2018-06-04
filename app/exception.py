from enum import IntEnum

i = 0


def count():
    global i
    i += 1
    return i


class RailRoadAPIError(IntEnum):
    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj

    UNKNOWN_ERROR_CODE = (i, 'UNKNOWN_ERROR_CODE phrase', 'UNKNOWN_ERROR_CODE description')
    PRIVATE_METHOD = (count(), 'PRIVATE_METHOD phrase', 'PRIVATE_METHOD description')
    BAD_ACCEPT_LANGUAGE_HEADER = (count(), 'BAD_ACCEPT_LANGUAGE_HEADER phrase', 'BAD_ACCEPT_LANGUAGE_HEADER description')

    BAD_USER_IDENTITY = (count(), 'BAD_USER_IDENTITY phrase', 'BAD_USER_IDENTITY description')
    USER_EMAIL_BUSY = (count(), 'USER_EMAIL_BUSY phrase', 'USER_EMAIL_BUSY description')
    USER_NOT_EXIST = (count(), 'USER_NOT_EXIST phrase', 'USER_NOT_EXIST description')

    BAD_SERVER_IDENTITY = (count(), 'BAD_SERVER_IDENTITY phrase', 'BAD_SERVER_IDENTITY description')

    REQUEST_NO_JSON = (count(), 'REQUEST_NO_JSON phrase', 'REQUEST_NO_JSON description')

    VPNSERVER_IDENTIFIER_ERROR = (count(), 'VPNSERVER_IDENTIFIER_ERROR phrase', 'VPNSERVER_IDENTIFIER_ERROR description')
