"""
Module defining the CrawledPage domain entity.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CrawledPage:
    """
    Represents the extracted content and metadata of a crawled webpage.
    """

    url: str
    title: str
    markdown_content: str
    character_count: int
    depth: int = 0
