"""
Unit tests for ManageExclusionsUseCase.
"""

from Src.Features.Scraper.UseCases.ManageExclusionsUseCase import ManageExclusionsUseCase


def test_IsExcluded_WithPrefixPattern_ExcludesMatchingUrls():
    manager = ManageExclusionsUseCase()
    manager.add_exclusion("amazon.com/bola/kula")

    assert manager.is_excluded("https://amazon.com/bola/kula/item1") is True
    assert manager.is_excluded("https://amazon.com/bola/kula") is True
    assert manager.is_excluded("https://amazon.com/bola/other") is False
    assert manager.is_excluded("https://amazon.com/home") is False


def test_IsExcluded_WithPathPattern_ExcludesMatchingUrls():
    manager = ManageExclusionsUseCase()
    manager.add_exclusion("/bola/kula")

    assert manager.is_excluded("https://amazon.com/bola/kula/product-1") is True
    assert manager.is_excluded("https://amazon.com/bola/other") is False


def test_UndoLastExclusion_WithExclusionAdded_RestoresPreviousState():
    manager = ManageExclusionsUseCase()
    manager.add_exclusion("/legacy")
    manager.add_exclusion("amazon.com/bola/kula")

    assert manager.is_excluded("https://amazon.com/bola/kula/item") is True
    assert manager.is_excluded("https://amazon.com/legacy/page") is True

    undone = manager.undo_last_exclusion()
    assert undone == "amazon.com/bola/kula"
    assert manager.is_excluded("https://amazon.com/bola/kula/item") is False
    assert manager.is_excluded("https://amazon.com/legacy/page") is True


def test_FilterUrls_WithActiveExclusions_ReturnsOnlyNonMatchingUrls():
    manager = ManageExclusionsUseCase()
    manager.add_exclusion("amazon.com/bola/kula")

    urls = [
        "https://amazon.com/bola/kula/item1",
        "https://amazon.com/bola/kula/item2",
        "https://amazon.com/bola/allowed",
        "https://amazon.com/docs/intro",
    ]

    filtered = manager.filter_urls(urls)
    assert filtered == [
        "https://amazon.com/bola/allowed",
        "https://amazon.com/docs/intro",
    ]


def test_AddExclusion_WithDuplicatePattern_IgnoresDuplicate():
    manager = ManageExclusionsUseCase()
    assert manager.add_exclusion("/docs/legacy") is True
    assert manager.add_exclusion("/docs/legacy") is False
    assert len(manager.get_active_exclusions()) == 1


def test_IsExcluded_WithUserReportedUrlPattern_ExcludesTargetAndSubpaths():
    manager = ManageExclusionsUseCase()
    manager.add_exclusion("https://palmirymoje.pl/kalendarz-ogrodnika")

    assert manager.is_excluded("https://palmirymoje.pl/kalendarz-ogrodnika") is True
    assert manager.is_excluded("https://palmirymoje.pl/kalendarz-ogrodnika/") is True
    assert manager.is_excluded("https://palmirymoje.pl/kalendarz-ogrodnika/maj") is True
    assert manager.is_excluded("https://palmirymoje.pl/o-nas") is False
    assert manager.is_excluded("https://palmirymoje.pl/kontakt") is False


def test_IsExcluded_WithRelativeSubpathAndBasePrefix_ExcludesTargetAndSubpaths():
    manager = ManageExclusionsUseCase(base_path_prefix="/buka")
    manager.add_exclusion("/legacy")

    assert manager.is_excluded("https://amazon.com/buka/legacy") is True
    assert manager.is_excluded("https://amazon.com/buka/legacy/") is True
    assert manager.is_excluded("https://amazon.com/buka/legacy/v1") is True
    assert manager.is_excluded("https://amazon.com/buka/active") is False


