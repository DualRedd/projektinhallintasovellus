from enum import Enum
class task_state(Enum):
    Pending = "Pending"
    InProgress = 'In Progress'
    Completed = 'Completed'
    Archived = 'Archived'