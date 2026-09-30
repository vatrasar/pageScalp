"""
Screen: SummaryScreen
Purpose: Presents final execution results, statistics, output files, and NotebookLM guidance.
Available Functionalities:
  - Display crawl summary table
  - Display NotebookLM usage instructions
Key UI elements:
  - BannerComponent
  - StatsTableComponent
  - NotebookLM Guide Panel
Navigation:
  - Navigate From: DashboardScreen
  - Navigate To: Application Exit
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from Src.Features.Scraper.Domain.CrawlStatistics import CrawlStatistics
from Src.Features.Scraper.UI.FeatureComponents.BannerComponent import BannerComponent
from Src.Features.Scraper.UI.FeatureComponents.StatsTableComponent import StatsTableComponent


class SummaryScreen:
    """
    Renders the final summary report and NotebookLM integration instructions.
    """

    def __init__(self, console: Console) -> None:
        self._console = console
        self._banner = BannerComponent()
        self._stats_table = StatsTableComponent()

    def display(self, statistics: CrawlStatistics) -> None:
        """
        Renders the complete end-of-run summary and instruction card to the terminal.
        
        Invoked by:
        - main.py upon successful crawl workflow conclusion.
        """
        self._console.print(self._banner.render())
        self._console.print(self._stats_table.render(statistics))
        self._console.print("\n")
        self._console.print(self._build_notebooklm_guide_panel(statistics))

    def _build_notebooklm_guide_panel(self, statistics: CrawlStatistics) -> Panel:
        guide_text = Text()
        guide_text.append("💡 How to import into Google NotebookLM:\n\n", style="bright_yellow bold")
        guide_text.append("1. Open Google NotebookLM (", style="white")
        guide_text.append("https://notebooklm.google.com", style="cyan underline")
        guide_text.append(") and create or open your notebook.\n", style="white")
        guide_text.append("2. Click ", style="white")
        guide_text.append("'+ Add Source'", style="bold green")
        guide_text.append(" -> Select ", style="white")
        guide_text.append("'Upload Sources / Markdown'.\n", style="bold magenta")
        guide_text.append("3. Select your generated file(s):\n", style="white")

        for file_path in statistics.generated_files:
            guide_text.append(f"   📂 {file_path}\n", style="bold cyan")

        guide_text.append(
            "\n✨ All pages have been cleaned of navigation clutter, formatted with clean headers, and indexed with a Table of Contents!",
            style="green bold",
        )

        return Panel(
            guide_text,
            title="[bold green]✔ Crawl Complete — Ready for NotebookLM[/]",
            border_style="green",
            padding=(1, 2),
        )
