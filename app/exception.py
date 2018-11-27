import sys

sys.path.insert(0, '../rest_api_library')
from response import APIErrorEnum

name = 'RRNAPI-'
i = 0


def count():
    global i
    i += 1
    return i


def get_all_error_codes():
    return [e.code for e in RailRoadAPIError]


class RailRoadAPIError(APIErrorEnum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    UNKNOWN_ERROR_CODE = (name + str(count()), 'UNKNOWN_ERROR_CODE phrase', 'UNKNOWN_ERROR_CODE description')
    METHOD_NOT_ALLOWED = (name + str(count()), 'METHOD_NOT_ALLOWED phrase', 'METHOD_NOT_ALLOWED description')
    PRIVATE_METHOD = (name + str(count()), 'PRIVATE_METHOD phrase', 'PRIVATE_METHOD description')
    BAD_ACCEPT_LANGUAGE_HEADER = (name + str(count()), 'BAD_ACCEPT_LANGUAGE_HEADER phrase', 'BAD_ACCEPT_LANGUAGE_HEADER description')
    BAD_IDENTITY_ERROR = (name + str(count()), 'BAD_IDENTITY_ERROR phrase', 'BAD_IDENTITY_ERROR description')

    API_DOES_NOT_EXIST = (name + str(count()), 'API_DOES_NOT_EXIST phrase', 'API_DOES_NOT_EXIST description')

    USER_EMAIL_BUSY = (name + str(count()), 'USER_EMAIL_BUSY phrase', 'USER_EMAIL_BUSY description')
    USER_NOT_EXIST = (name + str(count()), 'USER_NOT_EXIST phrase', 'USER_NOT_EXIST description')

    PINCODE_NOT_EXIST = (name + str(count()), 'PINCODE_NOT_EXIST phrase', 'PINCODE_NOT_EXIST description')

    USER_SUBSCRIPTION_NOT_EXIST = (name + str(count()), 'USER_SUBSCRIPTION_NOT_EXIST phrase', 'USER_SUBSCRIPTION_NOT_EXIST description')

    PAYMENT_BAD_DATA_ERROR = (name + str(count()), 'PAYMENT_BAD_DATA_ERROR phrase', 'PAYMENT_BAD_DATA_ERROR description')

    REQUEST_NO_JSON = (name + str(count()), 'REQUEST_NO_JSON phrase', 'REQUEST_NO_JSON description')

    PAYMENT_DOES_NOT_UPDATE_ORDER = (name + str(count()), 'Order does not update for payment', 'We create payment, but did not link this payment with order')

    PAYMENT_APN_DOES_NOT_CONTAIN_ORDER_CODE_CUSTOM_FIELD = (name + str(count()), 'APN does not contain ordercode custom field', 'We received APN but without x-ordercode custom field for some reason. Need manual work')
    PAYMENT_APN_DOES_NOT_CONTAIN_USER_UUID_CUSTOM_FIELD = (name + str(count()), 'APN does not contain useruuid custom field', 'We received APN but without x-useruuid custom field for some reason. Need manual work')
    PAYMENT_APN_DID_NOT_FIND_USER_SUB = (name + str(count()), 'APN is okay, but ', 'We received APN, get all user services by user uuid from x-useruuid custom field, but did not find user subscription for what this payment come. Need manual work')

    VPNTYPES_IDENTIFIER_ERROR = (name + str(count()), 'VPNTYPES_IDENTIFIER_ERROR phrase', 'VPNTYPES_IDENTIFIER_ERROR description')
    DEVICEPLATFORMS_IDENTITY_ERROR = (name + str(count()), 'DEVICEPLATFORMS_IDENTITY_ERROR phrase', 'DEVICEPLATFORMS_IDENTITY_ERROR description')


class UserPolicyException(Exception):
    __version__ = 1

    error = None
    error_code = None
    developer_message = None

    def __init__(self, error: str, error_code: int, developer_message: str = None, *args):
        super().__init__(*args)
        self.error = error
        self.error_code = error_code
        self.developer_message = developer_message
