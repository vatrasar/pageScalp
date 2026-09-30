"""
Module defining the CrawlConfiguration value object.
"""

from dataclasses import dataclass, field
from typing import Set, List
from Src.Features.Scraper.Domain.CrawlScopeMode import CrawlScopeMode


@dataclass(frozen=True)
class CrawlConfiguration:
    """
    Holds configuration parameters governing a crawl execution.
    """

    seed_url: str
    scope_mode: CrawlScopeMode = CrawlScopeMode.PATH_PREFIX
    path_prefix: str = ""
    allowed_domains: Set[str] = field(default_factory=set)
    excluded_patterns: List[str] = field(default_factory=list)
    max_pages: int = 100
    max_characters_per_file: int = 1000000
    output_destination: str = "scraped_documentation.md"
    concurrency: int = 5
    delay_seconds: float = 0.1
    enable_review: bool = True
