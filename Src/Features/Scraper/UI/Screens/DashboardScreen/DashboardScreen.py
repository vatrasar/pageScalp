"""
Screen: DashboardScreen
Purpose: Displays live visual feedback during crawl execution including spinners, progress, and metrics.
Available Functionalities:
  - Real-time progress updates
  - Live activity logging
  - Terminal screen refresh
Key UI elements:
  - BannerComponent
  - Progress bar with spinners
  - UrlStatusTableComponent
Navigation:
  - Navigate From: SetupScreen / main.py
  - Navigate To: SummaryScreen
"""

from typing import Optional
from rich.console import Console, Group
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from Src.Features.Scraper.Domain.CrawlStatistics import CrawlStatistics
from Src.Features.Scraper.Domain.CrawlConfiguration import CrawlConfiguration
from Src.Features.Scraper.UI.FeatureComponents.BannerComponent import BannerComponent
from Src.Features.Scraper.UI.FeatureComponents.UrlStatusTableComponent import UrlStatusTableComponent


class DashboardScreen:
    """
    Manages the live terminal interface during crawl processing.
    """

    def __init__(self, console: Console, configuration: CrawlConfiguration) -> None:
        self._console = console
        self._configuration = configuration
        self._banner = BannerComponent()
        self._status_component = UrlStatusTableComponent()
        self._progress = Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style="bright_blue", complete_style="green bold"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self._console,
        )
        self._task_id = self._progress.add_task("Crawling pages...", total=configuration.max_pages)
        self._live: Optional[Live] = None

    def start(self) -> None:
        """
        Initializes the live rendering context in the terminal.
        
        Invoked by:
        - main.py before initiating crawl execution.
        """
        layout = self._build_layout("Starting crawler...", CrawlStatistics())
        self._live = Live(layout, console=self._console, refresh_per_second=10)
        self._live.start()

    def stop(self) -> None:
        """
        Terminates the live rendering context.
        
        Invoked by:
        - main.py after crawl execution completes.
        """
        if self._live:
            self._live.stop()
            self._live = None

    def update(self, current_action: str, statistics: CrawlStatistics) -> None:
        """
        Refreshes the live layout with updated crawl actions and statistics.
        
        Invoked by:
        - CrawlWebsiteUseCase progress callback.
        """
        if not self._live:
            return

        self._progress.update(
            self._task_id,
            completed=statistics.crawled_pages_count,
            description=f"[cyan]Pages: {statistics.crawled_pages_count}/{self._configuration.max_pages}[/]",
        )
        layout = self._build_layout(current_action, statistics)
        self._live.update(layout)

    def _build_layout(self, current_action: str, statistics: CrawlStatistics) -> Group:
        status_panel = self._status_component.render(current_action, statistics)
        return Group(
            self._banner.render(),
            self._progress,
            status_panel,
        )
