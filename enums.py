from enum import Enum


class TaskType(Enum):
    WORK  = 0
    LUNCH = 1
    BREAK = 2

class ActionType(Enum):
    IN  = 1
    OUT = 0