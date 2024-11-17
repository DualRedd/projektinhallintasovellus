from enum import Enum
class RoleEnum(Enum):
    Observer = 0
    Participant = 1
    Member = 2
    Co_owner = 3
    Owner = 4

    @classmethod
    def has_value(cls, value : int):
        return value in cls._value2member_map_