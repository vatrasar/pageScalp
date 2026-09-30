"""
Unit tests for FilterUrlUseCase.
"""

from Src.Features.Scraper.Domain.CrawlConfiguration import CrawlConfiguration
from Src.Features.Scraper.Domain.CrawlScopeMode import CrawlScopeMode
from Src.Features.Scraper.UseCases.FilterUrlUseCase import FilterUrlUseCase


def test_IsAllowed_WithExternalDomain_ReturnsFalse():
    config = CrawlConfiguration(
        seed_url="https://amazon.com/buka",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
    )
    use_case = FilterUrlUseCase(config)

    assert use_case.is_allowed("https://empik.com/buka") is False
    assert use_case.is_allowed("https://google.com") is False


def test_IsAllowed_WithSameDomainDifferentPrefix_ReturnsFalse():
    config = CrawlConfiguration(
        seed_url="https://amazon.com/buka",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
    )
    use_case = FilterUrlUseCase(config)

    assert use_case.is_allowed("https://amazon.com/other") is False
    assert use_case.is_allowed("https://amazon.com/") is False
    assert use_case.is_allowed("https://amazon.com/bukanier") is False


def test_IsAllowed_WithSameDomainMatchingPrefix_ReturnsTrue():
    config = CrawlConfiguration(
        seed_url="https://amazon.com/buka",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
    )
    use_case = FilterUrlUseCase(config)

    assert use_case.is_allowed("https://amazon.com/buka") is True
    assert use_case.is_allowed("https://amazon.com/buka/") is True
    assert use_case.is_allowed("https://amazon.com/buka/item-123") is True
    assert use_case.is_allowed("https://amazon.com/buka/category/nested") is True


def test_IsAllowed_WithDisallowedAssetExtension_ReturnsFalse():
    config = CrawlConfiguration(
        seed_url="https://amazon.com/buka",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
    )
    use_case = FilterUrlUseCase(config)

    assert use_case.is_allowed("https://amazon.com/buka/image.png") is False
    assert use_case.is_allowed("https://amazon.com/buka/manual.pdf") is False
    assert use_case.is_allowed("https://amazon.com/buka/archive.zip") is False
    assert use_case.is_allowed("https://amazon.com/buka/script.js") is False


def test_IsAllowed_WithNonHttpScheme_ReturnsFalse():
    config = CrawlConfiguration(
        seed_url="https://amazon.com/buka",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
    )
    use_case = FilterUrlUseCase(config)

    assert use_case.is_allowed("mailto:support@amazon.com") is False
    assert use_case.is_allowed("javascript:void(0)") is False


def test_NormalizeUrl_WithFragmentAndTrackingQuery_ReturnsCleanUrl():
    config = CrawlConfiguration(
        seed_url="https://amazon.com/buka",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
    )
    use_case = FilterUrlUseCase(config)

    raw_url = "https://amazon.com/buka/page?utm_source=twitter&id=42&ref=banner#section-2"
    normalized = use_case.normalize_url(raw_url)

    assert normalized == "https://amazon.com/buka/page?id=42"


def test_IsAllowed_WithConfiguredExclusionPattern_ReturnsFalse():
    config = CrawlConfiguration(
        seed_url="https://amazon.com/buka",
        scope_mode=CrawlScopeMode.PATH_PREFIX,
        excluded_patterns=["amazon.com/buka/kula", "/buka/legacy"],
    )
    use_case = FilterUrlUseCase(config)

    assert use_case.is_allowed("https://amazon.com/buka/kula/item1") is False
    assert use_case.is_allowed("https://amazon.com/buka/legacy/doc") is False
    assert use_case.is_allowed("https://amazon.com/buka/allowed") is True

