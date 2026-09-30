"""
Module containing the ExtractLinksUseCase for extracting URLs from HTML documents.
"""

from urllib.parse import urljoin
from typing import Set
from bs4 import BeautifulSoup


class ExtractLinksUseCase:
    """
    Parses an HTML document and extracts all hyperlinks resolved as absolute URLs.
    
    Invoked by:
    - CrawlWebsiteUseCase
    - Automated unit tests in test_extract_links.py
    """

    def execute(self, html_content: str, base_url: str) -> Set[str]:
        """
        Extracts and resolves all href targets found in the supplied HTML content.
        
        Invoked by:
        - CrawlWebsiteUseCase when processing fetched pages.
        """
        if not html_content or not base_url:
            return set()

        soup = BeautifulSoup(html_content, "lxml")
        discovered_urls: Set[str] = set()

        for anchor in soup.find_all("a", href=True):
            resolved = self._resolve_anchor_href(anchor["href"], base_url)
            if resolved:
                discovered_urls.add(resolved)

        return discovered_urls

    def _resolve_anchor_href(self, raw_href: str, base_url: str) -> str:
        clean_href = raw_href.strip()
        if not clean_href or clean_href.startswith("#"):
            return ""

        lower_href = clean_href.lower()
        if lower_href.startswith("javascript:") or lower_href.startswith("mailto:") or lower_href.startswith("tel:"):
            return ""

        return urljoin(base_url, clean_href)
