"""
Application entrypoint and CLI interface for PageScalp.
"""

import sys
import os
import asyncio
import argparse
from urllib.parse import urlparse
from typing import Optional, List
from rich.console import Console
from Src.Features.Scraper.Domain.CrawlConfiguration import CrawlConfiguration
from Src.Features.Scraper.Domain.CrawlScopeMode import CrawlScopeMode
from Src.Features.Scraper.UI.FeatureStyles.ConsoleTheme import APP_THEME
from Src.Features.Scraper.UI.Screens.SetupScreen import SetupScreen
from Src.Features.Scraper.UI.Screens.DashboardScreen import DashboardScreen
from Src.Features.Scraper.UI.Screens.LinkReviewScreen import LinkReviewScreen
from Src.Features.Scraper.UI.Screens.SummaryScreen import SummaryScreen
from Src.Features.Scraper.UseCases.CrawlWebsiteUseCase import CrawlWebsiteUseCase
from Src.Features.Scraper.UseCases.ManageExclusionsUseCase import ManageExclusionsUseCase


def parse_command_line_arguments() -> argparse.Namespace:
    """
    Parses CLI flags and positional arguments passed to the application.
    
    Invoked by:
    - main execution block
    """
    parser = argparse.ArgumentParser(
        prog="pagescalp",
        description="High-speed documentation crawler & Markdown generator for Google NotebookLM",
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=None,
        help="Seed website/documentation URL (e.g. https://amazon.com/buka)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Target output markdown file (default: derived from URL)",
    )
    parser.add_argument(
        "-p", "--prefix",
        default="",
        help="Path prefix to restrict crawling to (default: seed URL path)",
    )
    parser.add_argument(
        "-e", "--exclude",
        action="append",
        default=[],
        help="Path or URL pattern to exclude (can be specified multiple times)",
    )
    parser.add_argument(
        "-m", "--max-pages",
        type=int,
        default=100,
        help="Maximum number of pages to crawl (default: 100)",
    )
    parser.add_argument(
        "-c", "--max-chars",
        type=int,
        default=1000000,
        help="Maximum characters per file before splitting (default: 1,000,000)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=5,
        help="Number of concurrent worker tasks (default: 5)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.1,
        help="Polite delay between requests in seconds (default: 0.1)",
    )
    parser.add_argument(
        "--no-review",
        action="store_true",
        help="Bypass interactive link review screen before compiling markdown",
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Launch interactive setup wizard",
    )
    return parser.parse_args()


def build_configuration_from_arguments(args: argparse.Namespace) -> CrawlConfiguration:
    parsed = urlparse(args.url)
    prefix = args.prefix if args.prefix else parsed.path.rstrip("/")
    output_destination = args.output if args.output else _derive_default_filename(parsed.netloc, prefix)

    return CrawlConfiguration(
        seed_url=args.url,
        scope_mode=CrawlScopeMode.PATH_PREFIX,
        path_prefix=prefix,
        excluded_patterns=args.exclude,
        max_pages=args.max_pages,
        max_characters_per_file=args.max_chars,
        output_destination=output_destination,
        concurrency=args.concurrency,
        delay_seconds=args.delay,
        enable_review=not args.no_review,
    )


def _derive_default_filename(host: str, prefix: str) -> str:
    clean_host = host.replace("www.", "").split(":")[0]
    clean_prefix = prefix.replace("/", "_").strip("_")
    base = f"{clean_host}_{clean_prefix}" if clean_prefix else clean_host
    return f"{base}_documentation.md"


async def run_crawl_session(configuration: CrawlConfiguration, console: Console) -> None:
    dashboard = DashboardScreen(console, configuration)
    review_screen = LinkReviewScreen(console)

    dashboard.start()

    async def handle_link_review(urls: List[str], exclusions_manager: ManageExclusionsUseCase) -> List[str]:
        dashboard.stop()
        return await review_screen.review_urls(urls, exclusions_manager)

    crawler = CrawlWebsiteUseCase(
        configuration=configuration,
        progress_callback=dashboard.update,
        review_callback=handle_link_review,
    )

    try:
        pages, statistics = await crawler.execute()
    finally:
        dashboard.stop()

    summary = SummaryScreen(console)
    summary.display(statistics)


def main() -> None:
    """
    Main application entrypoint. Coordinates argument parsing, wizard launch, and async runtime.
    
    Invoked by:
    - CLI command execution
    """
    console = Console(theme=APP_THEME)
    args = parse_command_line_arguments()

    if args.interactive or not args.url:
        setup_screen = SetupScreen(console)
        configuration = setup_screen.prompt_configuration()
        if not configuration:
            console.print("\n[yellow]Crawl session cancelled by user.[/yellow]")
            sys.exit(0)
    else:
        configuration = build_configuration_from_arguments(args)

    try:
        asyncio.run(run_crawl_session(configuration, console))
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Crawl aborted by user. Output files preserved.[/bold yellow]")


if __name__ == "__main__":
    main()
