"""
Module defining the PageFetchDTO for network communication results.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class PageFetchDTO:
    """
    Data transfer object encapsulating the network response of a webpage request.
    """

    url: str
    status_code: int
    content: str
    headers: Dict[str, str]
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """
        Determines whether the network request completed successfully.
        Invoked by CrawlWebsiteUseCase to check fetch outcomes.
        """
        return self.status_code >= 200 and self.status_code < 300 and self.error_message is None
