"""
Module containing ExportMarkdownUseCase for compiling and chunking markdown documentation.
"""

import os
import re
from typing import List
from Src.Features.Scraper.Domain.CrawledPage import CrawledPage


class ExportMarkdownUseCase:
    """
    Compiles crawled pages into a single consolidated Markdown document with a Table of Contents,
    splitting into sequential self-contained parts when exceeding the configured character limit.
    
    Invoked by:
    - CrawlWebsiteUseCase
    - Automated unit tests in test_export_markdown.py
    """

    def execute(
        self,
        pages: List[CrawledPage],
        output_destination: str,
        max_characters_per_file: int = 1000000,
    ) -> List[str]:
        """
        Compiles the list of crawled pages to disk and returns the written file paths.
        
        Invoked by:
        - CrawlWebsiteUseCase upon crawl completion.
        """
        if not pages:
            return []

        self._ensure_output_directory(output_destination)
        page_chunks = self._partition_pages(pages, max_characters_per_file)
        written_filepaths: List[str] = []

        total_parts = len(page_chunks)
        for index, chunk in enumerate(page_chunks, start=1):
            filepath = self._derive_part_filepath(output_destination, index, total_parts)
            content = self._render_document(chunk, index, total_parts)
            self._write_file(filepath, content)
            written_filepaths.append(filepath)

        return written_filepaths

    def _ensure_output_directory(self, target_filepath: str) -> None:
        directory = os.path.dirname(target_filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def _partition_pages(
        self,
        pages: List[CrawledPage],
        max_characters: int,
    ) -> List[List[CrawledPage]]:
        chunks: List[List[CrawledPage]] = []
        current_chunk: List[CrawledPage] = []
        current_character_count = 0

        for page in pages:
            estimated_page_size = page.character_count + len(page.title) + len(page.url) + 120
            would_exceed_limit = (
                current_character_count + estimated_page_size > max_characters
                and len(current_chunk) > 0
            )

            if would_exceed_limit:
                chunks.append(current_chunk)
                current_chunk = [page]
                current_character_count = estimated_page_size
            else:
                current_chunk.append(page)
                current_character_count += estimated_page_size

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _derive_part_filepath(self, base_path: str, part_number: int, total_parts: int) -> str:
        if total_parts <= 1:
            return base_path

        root_name, extension = os.path.splitext(base_path)
        ext = extension if extension else ".md"
        return f"{root_name}_part{part_number}{ext}"

    def _render_document(
        self,
        chunk: List[CrawledPage],
        part_number: int,
        total_parts: int,
    ) -> str:
        blocks: List[str] = []
        part_suffix = f" (Part {part_number} of {total_parts})" if total_parts > 1 else ""
        header = f"# Documentation{part_suffix}\n\n"
        meta = f"> Total Pages in this section: {len(chunk)}\n\n"
        blocks.append(header)
        blocks.append(meta)

        blocks.append("## Table of Contents\n\n")
        for idx, page in enumerate(chunk, start=1):
            slug = self._generate_slug(page.title, idx)
            blocks.append(f"{idx}. [{page.title}](#{slug})\n")
        blocks.append("\n---\n\n")

        for idx, page in enumerate(chunk, start=1):
            slug = self._generate_slug(page.title, idx)
            page_section = (
                f'<a id="{slug}"></a>\n\n'
                f"## {idx}. {page.title}\n\n"
                f"> **Source:** [{page.url}]({page.url})\n\n"
                f"{page.markdown_content}\n\n"
                f"---\n\n"
            )
            blocks.append(page_section)

        return "".join(blocks)

    def _generate_slug(self, text: str, index: int) -> str:
        sanitized = re.sub(r"[^\w\s-]", "", text).strip().lower()
        slug = re.sub(r"[-\s]+", "-", sanitized)
        if not slug:
            return f"section-{index}"
        return f"sec-{index}-{slug}"

    def _write_file(self, filepath: str, content: str) -> None:
        with open(filepath, "w", encoding="utf-8") as file_handle:
            file_handle.write(content)
