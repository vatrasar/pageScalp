"""
Unit tests for ExportMarkdownUseCase.
"""

import os
from Src.Features.Scraper.Domain.CrawledPage import CrawledPage
from Src.Features.Scraper.UseCases.ExportMarkdownUseCase import ExportMarkdownUseCase


def test_ExportMarkdown_WithinLimit_GeneratesSingleFileWithToc(tmp_path):
    use_case = ExportMarkdownUseCase()
    destination = str(tmp_path / "combined_docs.md")

    pages = [
        CrawledPage(
            url="https://amazon.com/buka/p1",
            title="Introduction",
            markdown_content="Hello world this is page 1",
            character_count=26,
        ),
        CrawledPage(
            url="https://amazon.com/buka/p2",
            title="Getting Started",
            markdown_content="Installation steps for the app",
            character_count=30,
        ),
    ]

    result_files = use_case.execute(pages, destination, max_characters_per_file=50000)

    assert len(result_files) == 1
    assert result_files[0] == destination
    assert os.path.exists(destination)

    with open(destination, "r", encoding="utf-8") as file_handle:
        content = file_handle.read()

    assert "## Table of Contents" in content
    assert "1. [Introduction]" in content
    assert "2. [Getting Started]" in content
    assert "Hello world this is page 1" in content
    assert "Installation steps for the app" in content


def test_ExportMarkdown_ExceedingLimit_SplitsIntoSequentialPartsWithIndividualTocs(tmp_path):
    use_case = ExportMarkdownUseCase()
    destination = str(tmp_path / "split_docs.md")

    pages = [
        CrawledPage(
            url=f"https://amazon.com/buka/p{idx}",
            title=f"Page {idx}",
            markdown_content="X" * 300,
            character_count=300,
        )
        for idx in range(1, 6)
    ]

    result_files = use_case.execute(pages, destination, max_characters_per_file=600)

    assert len(result_files) > 1
    for filepath in result_files:
        assert os.path.exists(filepath)
        with open(filepath, "r", encoding="utf-8") as file_handle:
            file_content = file_handle.read()
        assert "## Table of Contents" in file_content
        assert "# Documentation (Part" in file_content


def test_ExportMarkdown_WithEmptyPages_ReturnsEmptyList(tmp_path):
    use_case = ExportMarkdownUseCase()
    destination = str(tmp_path / "empty.md")

    result = use_case.execute([], destination)
    assert result == []
    assert not os.path.exists(destination)
