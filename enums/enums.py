from enum import Enum
class role_enum(Enum):
    Observer = 0
    Collaborator = 1
    Manager = 2
    Co_owner = 3
    Owner = 4
    
    @classmethod
    def has_value(cls, value : int):
        return value in cls._value2member_map_
    
class task_state_enum(Enum):
    Pending = "Pending"
    InProgress = 'In Progress'
    Completed = 'Completed'
    Archived = 'Archived'

    @classmethod
    def has_value(cls, value : str):
        return value in cls._value2member_map_

class task_priority_enum(Enum):
    Low = 1
    Normal = 2
    High = 3
    Critical = 4

    @classmethod
    def has_value(cls, value : int):
        return value in cls._value2member_map_