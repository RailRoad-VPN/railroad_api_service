from enum import Enum

name = 'RRNAPI-'
i = 0


def count():
    global i
    i += 1
    return i


def get_all_error_codes():
    return [e.code for e in RailRoadAPIError]


class RailRoadAPIError(Enum):
    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, code, message, developer_message):
        self.code = code
        self.message = message
        self.developer_message = developer_message

    UNKNOWN_ERROR_CODE = (name + str(count()), 'UNKNOWN_ERROR_CODE phrase', 'UNKNOWN_ERROR_CODE description')
    PRIVATE_METHOD = (name + str(count()), 'PRIVATE_METHOD phrase', 'PRIVATE_METHOD description')
    BAD_ACCEPT_LANGUAGE_HEADER = (
    name + str(count()), 'BAD_ACCEPT_LANGUAGE_HEADER phrase', 'BAD_ACCEPT_LANGUAGE_HEADER description')

    BAD_USER_IDENTITY = (name + str(count()), 'BAD_USER_IDENTITY phrase', 'BAD_USER_IDENTITY description')
    USER_EMAIL_BUSY = (name + str(count()), 'USER_EMAIL_BUSY phrase', 'USER_EMAIL_BUSY description')
    USER_NOT_EXIST = (name + str(count()), 'USER_NOT_EXIST phrase', 'USER_NOT_EXIST description')

    USER_SUBSCRIPTION_NOT_EXIST = (
    name + str(count()), 'USER_SUBSCRIPTION_NOT_EXIST phrase', 'USER_SUBSCRIPTION_NOT_EXIST description')

    BAD_SERVER_IDENTITY = (name + str(count()), 'BAD_SERVER_IDENTITY phrase', 'BAD_SERVER_IDENTITY description')

    PAYMENT_BAD_DATA_ERROR = (
    name + str(count()), 'PAYMENT_BAD_DATA_ERROR phrase', 'PAYMENT_BAD_DATA_ERROR description')

    REQUEST_NO_JSON = (name + str(count()), 'REQUEST_NO_JSON phrase', 'REQUEST_NO_JSON description')

    VPNSERVER_IDENTIFIER_ERROR = (
    name + str(count()), 'VPNSERVER_IDENTIFIER_ERROR phrase', 'VPNSERVER_IDENTIFIER_ERROR description')
