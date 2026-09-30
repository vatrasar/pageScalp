"""
Component: UrlStatusTableComponent
Purpose: Renders a real-time status summary of current crawl activity in the dashboard.
Usage:
  - Inputs: current_action (str), statistics (CrawlStatistics)
  - Outputs: Rich Panel containing activity summary
  - Bindings: None
Key UI elements:
  - Current action ticker
  - Queue and progress counters
Used In:
  - DashboardScreen
"""

from rich.panel import Panel
from rich.table import Table
from Src.Features.Scraper.Domain.CrawlStatistics import CrawlStatistics


class UrlStatusTableComponent:
    """
    Renders real-time action and status panels during crawling.
    """

    def render(self, current_action: str, statistics: CrawlStatistics) -> Panel:
        """
        Builds a dynamic status panel illustrating the active crawl state.
        
        Invoked by:
        - DashboardScreen
        """
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan", width=18)
        table.add_column(style="white")

        table.add_row("Current Action:", f"[yellow]{current_action}[/]")
        table.add_row("Pages Crawled:", f"[green bold]{statistics.crawled_pages_count}[/]")
        table.add_row("URLs Discovered:", f"[bright_blue]{statistics.discovered_urls_count}[/]")
        table.add_row("Elapsed Time:", f"[white]{statistics.elapsed_seconds:.1f}s[/]")

        return Panel(
            table,
            title="[bold cyan]Live Activity[/]",
            border_style="cyan",
            padding=(0, 1),
        )
