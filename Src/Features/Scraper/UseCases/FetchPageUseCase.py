"""
Module containing FetchPageUseCase for performing HTTP network requests.
"""

from typing import Dict, Optional
import httpx
from Src.Features.Scraper.Domain.PageFetchDTO import PageFetchDTO


class FetchPageUseCase:
    """
    Performs asynchronous HTTP GET requests to fetch HTML content from web servers.
    
    Invoked by:
    - CrawlWebsiteUseCase
    """

    USER_AGENT = "Mozilla/5.0 (compatible; PageScalp/1.0; +https://github.com/pagescalp)"
    DEFAULT_TIMEOUT_SECONDS = 15.0

    def __init__(self, client: Optional[httpx.AsyncClient] = None) -> None:
        self._external_client = client

    async def execute(self, url: str) -> PageFetchDTO:
        """
        Executes an asynchronous HTTP GET request to retrieve the document at the provided URL.
        
        Invoked by:
        - CrawlWebsiteUseCase when processing crawl targets from the queue.
        """
        headers = {"User-Agent": self.USER_AGENT}
        if self._external_client:
            return await self._perform_fetch(self._external_client, url, headers)

        async with httpx.AsyncClient(follow_redirects=True, timeout=self.DEFAULT_TIMEOUT_SECONDS) as local_client:
            return await self._perform_fetch(local_client, url, headers)

    async def _perform_fetch(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Dict[str, str],
    ) -> PageFetchDTO:
        try:
            response = await client.get(url, headers=headers)
            content_type = response.headers.get("content-type", "").lower()
            if not self._is_html_content(content_type):
                return PageFetchDTO(
                    url=str(response.url),
                    status_code=response.status_code,
                    content="",
                    headers=dict(response.headers),
                    error_message=f"Ignored non-HTML content type: {content_type}",
                )

            return PageFetchDTO(
                url=str(response.url),
                status_code=response.status_code,
                content=response.text,
                headers=dict(response.headers),
            )
        except httpx.HTTPError as error:
            return PageFetchDTO(
                url=url,
                status_code=0,
                content="",
                headers={},
                error_message=f"HTTP request failed: {str(error)}",
            )
        except Exception as generic_error:
            return PageFetchDTO(
                url=url,
                status_code=0,
                content="",
                headers={},
                error_message=f"Unexpected network failure: {str(generic_error)}",
            )

    def _is_html_content(self, content_type: str) -> bool:
        if not content_type:
            return True
        return "text/html" in content_type or "application/xhtml+xml" in content_type
