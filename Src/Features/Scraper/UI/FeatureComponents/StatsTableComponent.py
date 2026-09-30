"""
Component: StatsTableComponent
Purpose: Renders a structured Rich table summarizing crawl execution performance metrics.
Usage:
  - Inputs: CrawlStatistics instance
  - Outputs: Rich Table object
  - Bindings: None
Key UI elements:
  - Metrics columns (Metric, Value)
  - Color-coded badges for status, counts, and generated file paths
Used In:
  - SummaryScreen
  - DashboardScreen
"""

from rich.table import Table
from Src.Features.Scraper.Domain.CrawlStatistics import CrawlStatistics


class StatsTableComponent:
    """
    Renders execution metrics into a tabular layout.
    """

    def render(self, statistics: CrawlStatistics) -> Table:
        """
        Constructs a Rich table displaying the crawl session metrics.
        
        Invoked by:
        - SummaryScreen
        - DashboardScreen
        """
        table = Table(
            title="Crawl Performance & Results",
            title_style="cyan bold",
            border_style="bright_blue",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Metric", style="white bold", width=28)
        table.add_column("Value", style="bright_cyan", width=42)

        table.add_row("Total Crawled Pages", f"[green bold]{statistics.crawled_pages_count}[/]")
        table.add_row("Total Discovered URLs", str(statistics.discovered_urls_count))
        table.add_row("Failed / Skipped URLs", f"[red]{statistics.failed_urls_count}[/]")
        table.add_row("Total Characters Extracted", f"{statistics.total_characters_count:,}")
        table.add_row("Elapsed Time", f"{statistics.elapsed_seconds:.2f} seconds")

        if statistics.generated_files:
            files_display = "\n".join(f"[bold green]✔[/] {f}" for f in statistics.generated_files)
            table.add_row("Generated Output Files", files_display)

        return table
