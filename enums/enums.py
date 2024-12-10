from enum import Enum
class role_enum(Enum):
    Observer = (0, "Observer")
    Collaborator = (1, "Collaborator")
    Manager = (2, "Manager")
    Co_owner = (3, "Co-owner")
    Owner = (4, "Owner")

    def __init__(self, value, display_name):
        self._value_ = value
        self.display_name = display_name

    def __lt__(self, other):
        if isinstance(other, role_enum):
            return self.value < other.value
        raise TypeError(f"'<' not supported between {type(self)} and {type(other)}")

    @classmethod
    def get_by_value(cls, value):
        for item in cls:
            if item.value == value:
                return item
        return None

class task_state_enum(Enum):
    Pending = (0, "Pending")
    InProgress = (1, "In Progress")
    Completed = (2, "Completed")
    Archived = (3, "Archived")

    def __init__(self, value, display_name):
        self._value_ = value
        self.display_name = display_name

    def __lt__(self, other):
        if isinstance(other, task_state_enum):
            return self.value < other.value
        raise TypeError(f"'<' not supported between {type(self)} and {type(other)}")

    @classmethod
    def get_by_value(cls, value):
        for item in cls:
            if item.value == value:
                return item
        return None

class task_priority_enum(Enum):
    Low = (1, "Low")
    Normal = (2, "Normal")
    High = (3, "High")
    Critical = (4, "Critical")

    def __init__(self, value, display_name):
        self._value_ = value
        self.display_name = display_name

    def __lt__(self, other):
        if isinstance(other, task_priority_enum):
            return self.value < other.value
        raise TypeError(f"'<' not supported between {type(self)} and {type(other)}")

    @classmethod
    def get_by_value(cls, value):
        for item in cls:
            if item.value == value:
                return item
        return None