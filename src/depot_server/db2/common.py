"""
This file contains definitions shared across multiple models
"""

from enum import StrEnum


class Condition(StrEnum):
    GOOD = "good"
    MONITOR = "monitor"
    REPAIR = "repair"
    GONE = "gone"
