"""
This file contains definitions shared across multiple models
"""

from enum import StrEnum

from tortoise import fields


class Condition(StrEnum):
    GOOD = "good"
    MONITOR = "monitor"
    REPAIR = "repair"
    GONE = "gone"


type UserIdField = fields.UUIDField
