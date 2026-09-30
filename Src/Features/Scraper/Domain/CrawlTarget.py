"""
Module defining the CrawlTarget domain entity.
"""

from dataclasses import dataclass
from Src.Features.Scraper.Domain.CrawlStatus import CrawlStatus


@dataclass(frozen=True)
class CrawlTarget:
    """
    Represents an individual URL target scheduled for crawling.
    """

    url: str
    depth: int = 0
    status: CrawlStatus = CrawlStatus.PENDING
