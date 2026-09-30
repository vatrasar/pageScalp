"""
Module defining execution states for crawl tasks.
"""

from enum import Enum, auto


class CrawlStatus(Enum):
    """
    Represents the operational status of an individual crawl target or session.
    """

    PENDING = auto()
    IN_PROGRESS = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()
