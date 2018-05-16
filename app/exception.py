from enum import IntEnum


class RailRoadAPIError(IntEnum):

    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj

    UNKNOWN_ERROR_CODE = (0, 'UNKNOWN_ERROR_CODE phrase', 'UNKNOWN_ERROR_CODE description')
    PRIVATE_METHOD = (1, 'PRIVATE_METHOD phrase', 'PRIVATE_METHOD description')

    BAD_USER_IDENTITY = (2, 'BAD_USER_IDENTITY phrase', 'BAD_USER_IDENTITY description')
    USER_EMAIL_BUSY = (3, 'USER_EMAIL_BUSY phrase', 'USER_EMAIL_BUSY description')
    USER_NOT_EXIST = (4, 'USER_NOT_EXIST phrase', 'USER_NOT_EXIST description')
