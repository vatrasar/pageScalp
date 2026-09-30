"""
Module containing the FilterUrlUseCase for URL validation and normalization.
"""

from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import posixpath
from typing import Set, Optional
from Src.Features.Scraper.Domain.CrawlScopeMode import CrawlScopeMode
from Src.Features.Scraper.Domain.CrawlConfiguration import CrawlConfiguration
from Src.Features.Scraper.UseCases.ManageExclusionsUseCase import ManageExclusionsUseCase


class FilterUrlUseCase:
    """
    Validates whether a discovered candidate URL is within the allowed crawl scope,
    respects path exclusion rules, and normalizes valid URLs for consistent deduplication.
    
    Invoked by:
    - CrawlWebsiteUseCase
    - Automated unit tests in test_filter_url.py
    """

    DISALLOWED_EXTENSIONS: Set[str] = {
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico",
        ".pdf", ".zip", ".tar", ".gz", ".tgz", ".rar", ".7z",
        ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".webm",
        ".css", ".js", ".mjs", ".ts",
        ".woff", ".woff2", ".ttf", ".eot", ".otf",
        ".xml", ".rss", ".atom", ".json", ".csv",
    }

    TRACKING_QUERY_PREFIXES: Set[str] = {
        "utm_", "ref", "fbclid", "gclid", "msclkid", "mc_eid"
    }

    def __init__(self, configuration: CrawlConfiguration) -> None:
        self._configuration = configuration
        self._seed_parsed = urlparse(configuration.seed_url)
        self._seed_host = self._seed_parsed.netloc.lower()
        self._base_path_prefix = self._derive_path_prefix(self._seed_parsed.path)
        self._exclusions_manager = ManageExclusionsUseCase(
            configuration.excluded_patterns,
            base_path_prefix=self._base_path_prefix,
        )

    def is_allowed(self, candidate_url: str) -> bool:
        """
        Determines whether a candidate URL satisfies the scoping, extension, and exclusion rules.
        
        Invoked by:
        - CrawlWebsiteUseCase during link processing.
        """
        parsed = urlparse(candidate_url)
        if not self._has_supported_scheme(parsed.scheme):
            return False

        if self._has_disallowed_extension(parsed.path):
            return False

        if self._exclusions_manager.is_excluded(candidate_url):
            return False

        return self._matches_scope_policy(parsed)

    def normalize_url(self, raw_url: str) -> Optional[str]:
        """
        Strips fragments and tracking query parameters to produce a canonical URL.
        
        Invoked by:
        - CrawlWebsiteUseCase before enqueuing discovered links.
        """
        if not raw_url:
            return None

        parsed = urlparse(raw_url)
        cleaned_query = self._filter_query_parameters(parsed.query)
        normalized_path = posixpath.normpath(parsed.path) if parsed.path else "/"
        if parsed.path.endswith("/") and not normalized_path.endswith("/"):
            normalized_path += "/"

        normalized_tuple = (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            normalized_path,
            parsed.params,
            cleaned_query,
            "",
        )
        return urlunparse(normalized_tuple)

    def get_exclusions_manager(self) -> ManageExclusionsUseCase:
        """
        Provides access to the underlying ManageExclusionsUseCase instance.
        
        Invoked by:
        - CrawlWebsiteUseCase
        """
        return self._exclusions_manager

    def _derive_path_prefix(self, raw_seed_path: str) -> str:
        if self._configuration.path_prefix:
            return self._configuration.path_prefix.rstrip("/")

        clean_path = raw_seed_path.rstrip("/")
        return clean_path

    def _has_supported_scheme(self, scheme: str) -> bool:
        return scheme.lower() in {"http", "https"}

    def _has_disallowed_extension(self, path: str) -> bool:
        lower_path = path.lower()
        return any(lower_path.endswith(ext) for ext in self.DISALLOWED_EXTENSIONS)

    def _matches_scope_policy(self, parsed) -> bool:
        candidate_host = parsed.netloc.lower()
        if self._configuration.scope_mode == CrawlScopeMode.PATH_PREFIX:
            return self._matches_strict_prefix(candidate_host, parsed.path)

        if self._configuration.scope_mode == CrawlScopeMode.SAME_DOMAIN:
            return candidate_host == self._seed_host

        return self._matches_custom_allowed(candidate_host, parsed.path)

    def _matches_strict_prefix(self, candidate_host: str, candidate_path: str) -> bool:
        if candidate_host != self._seed_host:
            return False

        if not self._base_path_prefix:
            return True

        normalized_candidate_path = posixpath.normpath(candidate_path)
        return (
            normalized_candidate_path == self._base_path_prefix
            or normalized_candidate_path.startswith(self._base_path_prefix + "/")
        )

    def _matches_custom_allowed(self, candidate_host: str, candidate_path: str) -> bool:
        if candidate_host in self._configuration.allowed_domains:
            return True

        return any(
            candidate_host.endswith("." + domain)
            for domain in self._configuration.allowed_domains
        )

    def _filter_query_parameters(self, raw_query: str) -> str:
        if not raw_query:
            return ""

        query_pairs = parse_qsl(raw_query, keep_blank_values=True)
        filtered_pairs = [
            (key, val) for key, val in query_pairs
            if not self._is_tracking_parameter(key)
        ]
        return urlencode(filtered_pairs)

    def _is_tracking_parameter(self, parameter_name: str) -> bool:
        lower_name = parameter_name.lower()
        return any(lower_name.startswith(prefix) for prefix in self.TRACKING_QUERY_PREFIXES)
