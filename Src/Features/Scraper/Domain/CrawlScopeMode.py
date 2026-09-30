"""
Module defining crawl scoping modes for boundary enforcement.
"""

from enum import Enum, auto


class CrawlScopeMode(Enum):
    """
    Defines the boundaries within which the crawler is permitted to operate.
    """

    PATH_PREFIX = auto()
    SAME_DOMAIN = auto()
    CUSTOM = auto()
