from enum import IntEnum
from typing import NamedTuple, TypedDict

from src.database.time_database_type import IconTuple, ReminderDataDict


class HourTuple(NamedTuple):
    hid: int
    name: str
    iid: IconTuple
    fid: int
    reminders: dict[int, ReminderDataDict]
    sums: int

class ReminderStatusEnum(IntEnum):
    DELETE = -1
    HOLD = 0
    NEW = 1
    MODIFY = 2

class Reminder(TypedDict):
    eid: int
    data: ReminderDataDict
    status: ReminderStatusEnum
