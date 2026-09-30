"""
Module containing CrawlWebsiteUseCase orchestrating the asynchronous crawl, link review, and markdown compilation.
"""

import asyncio
from typing import List, Set, Optional, Callable, Tuple
import httpx
from Src.Features.Scraper.Domain.CrawlConfiguration import CrawlConfiguration
from Src.Features.Scraper.Domain.CrawlStatistics import CrawlStatistics
from Src.Features.Scraper.Domain.CrawlTarget import CrawlTarget
from Src.Features.Scraper.Domain.CrawledPage import CrawledPage
from Src.Features.Scraper.Domain.CrawlStatus import CrawlStatus
from Src.Features.Scraper.UseCases.FilterUrlUseCase import FilterUrlUseCase
from Src.Features.Scraper.UseCases.ExtractLinksUseCase import ExtractLinksUseCase
from Src.Features.Scraper.UseCases.FetchPageUseCase import FetchPageUseCase
from Src.Features.Scraper.UseCases.ConvertHtmlToMarkdownUseCase import ConvertHtmlToMarkdownUseCase
from Src.Features.Scraper.UseCases.ExportMarkdownUseCase import ExportMarkdownUseCase
from Src.Features.Scraper.UseCases.ManageExclusionsUseCase import ManageExclusionsUseCase


class CrawlWebsiteUseCase:
    """
    Coordinates asynchronous webpage discovery, user link review/curation, and markdown export.
    
    Invoked by:
    - main.py CLI command handler
    - Automated integration tests
    """

    def __init__(
        self,
        configuration: CrawlConfiguration,
        progress_callback: Optional[Callable[[str, CrawlStatistics], None]] = None,
        review_callback: Optional[Callable[[List[str], ManageExclusionsUseCase], List[str]]] = None,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._configuration = configuration
        self._progress_callback = progress_callback
        self._review_callback = review_callback
        self._external_client = client
        self._filter_use_case = FilterUrlUseCase(configuration)
        self._extract_links_use_case = ExtractLinksUseCase()
        self._convert_markdown_use_case = ConvertHtmlToMarkdownUseCase()
        self._export_markdown_use_case = ExportMarkdownUseCase()
        self._visited_urls: Set[str] = set()
        self._crawled_pages: List[CrawledPage] = []
        self._statistics = CrawlStatistics()

    async def execute(self) -> Tuple[List[CrawledPage], CrawlStatistics]:
        """
        Executes the web crawl workflow from the seed URL, conducts review if enabled, and exports Markdown.
        
        Invoked by:
        - main.py CLI command handler
        """
        normalized_seed = self._filter_use_case.normalize_url(self._configuration.seed_url)
        if not normalized_seed or not self._filter_use_case.is_allowed(normalized_seed):
            self._statistics.mark_completed()
            return self._crawled_pages, self._statistics

        work_queue: asyncio.Queue[CrawlTarget] = asyncio.Queue()
        work_queue.put_nowait(CrawlTarget(url=normalized_seed, depth=0))
        self._visited_urls.add(normalized_seed)
        self._statistics.discovered_urls_count += 1

        semaphore = asyncio.Semaphore(self._configuration.concurrency)

        if self._external_client:
            fetch_use_case = FetchPageUseCase(self._external_client)
            await self._run_crawler_loop(work_queue, fetch_use_case, semaphore)
        else:
            timeout = httpx.Timeout(15.0)
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
                fetch_use_case = FetchPageUseCase(client)
                await self._run_crawler_loop(work_queue, fetch_use_case, semaphore)

        await self._conduct_link_review_if_requested()
        self._export_results()
        self._statistics.mark_completed()
        return self._crawled_pages, self._statistics

    async def _conduct_link_review_if_requested(self) -> None:
        if not self._review_callback or not self._configuration.enable_review:
            return

        discovered_urls = [p.url for p in self._crawled_pages]
        exclusions_manager = self._filter_use_case.get_exclusions_manager()
        if asyncio.iscoroutinefunction(self._review_callback):
            approved_urls = await self._review_callback(discovered_urls, exclusions_manager)
        else:
            approved_urls = self._review_callback(discovered_urls, exclusions_manager)

        approved_set = set(approved_urls)
        self._crawled_pages = [p for p in self._crawled_pages if p.url in approved_set]
        self._statistics.crawled_pages_count = len(self._crawled_pages)
        self._statistics.total_characters_count = sum(p.character_count for p in self._crawled_pages)

    async def _run_crawler_loop(
        self,
        work_queue: asyncio.Queue[CrawlTarget],
        fetch_use_case: FetchPageUseCase,
        semaphore: asyncio.Semaphore,
    ) -> None:
        active_tasks: Set[asyncio.Task] = set()

        while not work_queue.empty() or active_tasks:
            while not work_queue.empty() and self._can_spawn_worker(active_tasks):
                target = work_queue.get_nowait()
                task = asyncio.create_task(
                    self._process_single_target(target, work_queue, fetch_use_case, semaphore)
                )
                active_tasks.add(task)
                task.add_done_callback(active_tasks.discard)

            if not active_tasks:
                break

            await asyncio.sleep(0.02)

    def _can_spawn_worker(self, active_tasks: Set[asyncio.Task]) -> bool:
        has_reached_page_limit = len(self._crawled_pages) >= self._configuration.max_pages
        has_reached_concurrency_limit = len(active_tasks) >= self._configuration.concurrency
        return not has_reached_page_limit and not has_reached_concurrency_limit

    async def _process_single_target(
        self,
        target: CrawlTarget,
        work_queue: asyncio.Queue[CrawlTarget],
        fetch_use_case: FetchPageUseCase,
        semaphore: asyncio.Semaphore,
    ) -> None:
        async with semaphore:
            self._notify_progress(f"Fetching: {target.url}")
            fetch_dto = await fetch_use_case.execute(target.url)

            if not fetch_dto.is_success:
                self._statistics.failed_urls_count += 1
                return

            crawled_page = self._convert_markdown_use_case.execute(
                html_content=fetch_dto.content,
                url=fetch_dto.url,
                depth=target.depth,
            )

            if len(self._crawled_pages) >= self._configuration.max_pages:
                return

            self._crawled_pages.append(crawled_page)
            self._statistics.crawled_pages_count += 1
            self._statistics.total_characters_count += crawled_page.character_count

            if self._configuration.delay_seconds > 0:
                await asyncio.sleep(self._configuration.delay_seconds)

            if len(self._crawled_pages) < self._configuration.max_pages:
                self._discover_and_enqueue_links(fetch_dto.content, fetch_dto.url, target.depth, work_queue)

    def _discover_and_enqueue_links(
        self,
        html_content: str,
        base_url: str,
        current_depth: int,
        work_queue: asyncio.Queue[CrawlTarget],
    ) -> None:
        discovered_urls = self._extract_links_use_case.execute(html_content, base_url)
        for raw_url in discovered_urls:
            normalized = self._filter_use_case.normalize_url(raw_url)
            if not normalized:
                continue

            if normalized in self._visited_urls:
                continue

            if not self._filter_use_case.is_allowed(normalized):
                continue

            self._visited_urls.add(normalized)
            self._statistics.discovered_urls_count += 1
            work_queue.put_nowait(CrawlTarget(url=normalized, depth=current_depth + 1))

    def _export_results(self) -> None:
        written_paths = self._export_markdown_use_case.execute(
            pages=self._crawled_pages,
            output_destination=self._configuration.output_destination,
            max_characters_per_file=self._configuration.max_characters_per_file,
        )
        self._statistics.generated_files = written_paths

    def _notify_progress(self, current_action: str) -> None:
        if self._progress_callback:
            self._progress_callback(current_action, self._statistics)
