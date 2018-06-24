from enum import Enum


class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1000
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class EditorKeys(AutoNumber):
    ARROW_UP = ()
    ARROW_DOWN = ()
    ARROW_LEFT = ()
    ARROW_RIGHT = ()
    PAGE_UP = ()
    PAGE_DOWN = ()
    HOME_KEY = ()
    END_KEY = ()
    DEL_KEY = ()
