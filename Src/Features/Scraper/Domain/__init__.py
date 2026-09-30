"""
Domain layer models and enumerations for the Scraper feature.
"""

from Src.Features.Scraper.Domain.CrawlScopeMode import CrawlScopeMode
from Src.Features.Scraper.Domain.CrawlStatus import CrawlStatus
from Src.Features.Scraper.Domain.CrawlTarget import CrawlTarget
from Src.Features.Scraper.Domain.CrawledPage import CrawledPage
from Src.Features.Scraper.Domain.CrawlConfiguration import CrawlConfiguration
from Src.Features.Scraper.Domain.CrawlStatistics import CrawlStatistics
from Src.Features.Scraper.Domain.PageFetchDTO import PageFetchDTO

__all__ = [
    "CrawlScopeMode",
    "CrawlStatus",
    "CrawlTarget",
    "CrawledPage",
    "CrawlConfiguration",
    "CrawlStatistics",
    "PageFetchDTO",
]
