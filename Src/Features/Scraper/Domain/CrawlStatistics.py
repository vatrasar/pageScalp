"""
Module defining crawl execution metrics and statistics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class CrawlStatistics:
    """
    Accumulates runtime performance metrics and outcome tallies.
    """

    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    discovered_urls_count: int = 0
    crawled_pages_count: int = 0
    failed_urls_count: int = 0
    skipped_urls_count: int = 0
    total_characters_count: int = 0
    generated_files: List[str] = field(default_factory=list)

    def mark_completed(self) -> None:
        """
        Finalizes the crawl session by recording the completion timestamp.
        Invoked by CrawlWebsiteUseCase upon crawl termination.
        """
        self.end_time = datetime.now()

    @property
    def elapsed_seconds(self) -> float:
        """
        Calculates elapsed time in seconds from crawl start to finish or current moment.
        Invoked by UI components and summary screens to display runtime duration.
        """
        finish = self.end_time or datetime.now()
        return (finish - self.start_time).total_seconds()
