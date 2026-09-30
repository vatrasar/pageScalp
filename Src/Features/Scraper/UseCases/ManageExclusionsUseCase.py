"""
Module containing ManageExclusionsUseCase for tracking, applying, and undoing path exclusions.
"""

from urllib.parse import urlparse
from typing import List, Optional, Set


class ManageExclusionsUseCase:
    """
    Manages URL exclusion patterns with stateful undo history and applies filtering to URLs.
    Supports both domain-root paths and relative subpaths matching the seed path prefix.
    
    Invoked by:
    - LinkReviewScreen
    - FilterUrlUseCase
    - CrawlWebsiteUseCase
    - Automated unit tests in test_manage_exclusions.py
    """

    def __init__(
        self,
        initial_patterns: Optional[List[str]] = None,
        base_path_prefix: str = "",
    ) -> None:
        self._active_patterns: List[str] = []
        self._history_stack: List[str] = []
        self._base_path_prefix = base_path_prefix.strip().lower().rstrip("/")

        if initial_patterns:
            for pattern in initial_patterns:
                self.add_exclusion(pattern)

    def add_exclusion(self, raw_pattern: str) -> bool:
        """
        Registers a new exclusion pattern and pushes it onto the history stack.
        
        Invoked by:
        - LinkReviewScreen
        - SetupScreen
        """
        clean_pattern = raw_pattern.strip().lower()
        if not clean_pattern:
            return False

        if clean_pattern in self._active_patterns:
            return False

        self._active_patterns.append(clean_pattern)
        self._history_stack.append(clean_pattern)
        return True

    def undo_last_exclusion(self) -> Optional[str]:
        """
        Pops the most recent exclusion from the history stack and removes it from active patterns.
        
        Invoked by:
        - LinkReviewScreen
        """
        if not self._history_stack:
            return None

        last_pattern = self._history_stack.pop()
        if last_pattern in self._active_patterns:
            self._active_patterns.remove(last_pattern)

        return last_pattern

    def get_active_exclusions(self) -> List[str]:
        """
        Returns a copy of all currently active exclusion patterns.
        
        Invoked by:
        - LinkReviewScreen
        - StatsTableComponent
        """
        return list(self._active_patterns)

    def is_excluded(self, url: str) -> bool:
        """
        Evaluates whether a given URL matches any active exclusion pattern.
        
        Invoked by:
        - FilterUrlUseCase
        - LinkReviewScreen
        """
        if not self._active_patterns or not url:
            return False

        lower_url = url.lower()
        parsed = urlparse(lower_url)
        url_without_scheme = f"{parsed.netloc}{parsed.path}"

        for pattern in self._active_patterns:
            if self._matches_pattern(lower_url, url_without_scheme, parsed.path, pattern):
                return True

        return False

    def filter_urls(self, urls: List[str]) -> List[str]:
        """
        Filters a collection of URLs, retaining only those that do not match active exclusions.
        
        Invoked by:
        - LinkReviewScreen
        - CrawlWebsiteUseCase
        """
        return [url for url in urls if not self.is_excluded(url)]

    def _matches_pattern(
        self,
        full_url: str,
        url_without_scheme: str,
        url_path: str,
        pattern: str,
    ) -> bool:
        clean_pattern = pattern.strip().lower().rstrip("/")
        clean_full = full_url.lower().rstrip("/")
        clean_no_scheme = url_without_scheme.lower().rstrip("/")
        clean_path = url_path.lower().rstrip("/")

        candidates = [clean_full, clean_no_scheme, clean_path]
        prefixed_pattern = self._derive_prefixed_pattern(clean_pattern)

        for target in candidates:
            if target.startswith(clean_pattern):
                return True
            if prefixed_pattern and target.startswith(prefixed_pattern):
                return True

        if clean_pattern in clean_full:
            return True

        return False

    def _derive_prefixed_pattern(self, clean_pattern: str) -> Optional[str]:
        has_base_prefix = bool(self._base_path_prefix)
        is_subpath = clean_pattern.startswith("/") and not clean_pattern.startswith(self._base_path_prefix)
        if has_base_prefix and is_subpath:
            return f"{self._base_path_prefix}/{clean_pattern.lstrip('/')}".rstrip("/")
        return None
