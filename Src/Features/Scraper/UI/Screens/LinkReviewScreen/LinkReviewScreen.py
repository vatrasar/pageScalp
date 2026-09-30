"""
Screen: LinkReviewScreen
Purpose: Presents discovered links, enables adding/undoing exclusions interactively, and verifies the final list.
Available Functionalities:
  - Display discovered URLs and exclusion counts
  - Interactively add path/URL exclusion patterns using async prompt_toolkit
  - Undo recent exclusions
  - View full remaining and excluded URLs lists with pause-to-inspect
  - Confirm curated list for Markdown compilation
Key UI elements:
  - BannerComponent
  - Rich tables for active exclusions and remaining URLs
  - Questionary interactive menus and prompts (async)
Navigation:
  - Navigate From: CrawlWebsiteUseCase (post-discovery)
  - Navigate To: Markdown compilation
"""

from typing import List, Optional
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from Src.Features.Scraper.UseCases.ManageExclusionsUseCase import ManageExclusionsUseCase
from Src.Features.Scraper.UI.FeatureComponents.BannerComponent import BannerComponent


class LinkReviewScreen:
    """
    Guides the user through interactive curation and exclusion of discovered links.
    """

    def __init__(self, console: Console) -> None:
        self._console = console
        self._banner = BannerComponent()

    async def review_urls(
        self,
        discovered_urls: List[str],
        exclusions_manager: ManageExclusionsUseCase,
    ) -> List[str]:
        """
        Runs the interactive curation session asynchronously and returns the approved list of URLs to crawl and compile.
        
        Invoked by:
        - CrawlWebsiteUseCase before commencing markdown compilation.
        """
        while True:
            remaining_urls = exclusions_manager.filter_urls(discovered_urls)
            excluded_urls = [u for u in discovered_urls if exclusions_manager.is_excluded(u)]

            self._console.print(self._banner.render())
            self._render_curation_dashboard(discovered_urls, remaining_urls, exclusions_manager)

            action = await self._prompt_review_action(exclusions_manager, len(remaining_urls), len(excluded_urls))
            if action == "confirm":
                return remaining_urls

            if action == "cancel":
                return []

            if action == "add":
                await self._handle_add_exclusion(exclusions_manager, discovered_urls)
            elif action == "undo":
                await self._handle_undo_exclusion(exclusions_manager, discovered_urls)
            elif action == "view_remaining":
                await self._display_full_url_table("Remaining URLs to Copy", remaining_urls, "green")
            elif action == "view_excluded":
                await self._display_full_url_table("Excluded URLs", excluded_urls, "red")

    def _render_curation_dashboard(
        self,
        all_urls: List[str],
        remaining_urls: List[str],
        exclusions_manager: ManageExclusionsUseCase,
    ) -> None:
        summary_table = Table.grid(padding=(0, 2))
        summary_table.add_column(style="bold cyan", width=22)
        summary_table.add_column(style="white")

        active_rules = exclusions_manager.get_active_exclusions()
        rules_text = ", ".join(f"'{r}'" for r in active_rules) if active_rules else "[dim](none)[/dim]"

        summary_table.add_row("Total Discovered:", f"[bright_blue bold]{len(all_urls)}[/]")
        summary_table.add_row("Active Exclusions:", f"[yellow]{rules_text}[/]")
        summary_table.add_row("Remaining to Copy:", f"[green bold]{len(remaining_urls)}[/]")

        self._console.print("\n")
        self._console.print(
            Panel(
                summary_table,
                title="[bold cyan]Link Review & Curation[/]",
                border_style="cyan",
                padding=(1, 2),
            )
        )

        self._render_url_preview(remaining_urls)

    def _render_url_preview(self, remaining_urls: List[str]) -> None:
        preview_count = min(len(remaining_urls), 12)
        table = Table(
            title=f"Remaining URLs Preview ({len(remaining_urls)} total)",
            title_style="bold green",
            border_style="green",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("URL", style="white")

        for idx in range(preview_count):
            table.add_row(str(idx + 1), remaining_urls[idx])

        if len(remaining_urls) > preview_count:
            remaining_hidden = len(remaining_urls) - preview_count
            table.add_row(
                "...",
                f"[dim yellow]... and {remaining_hidden} more URLs. (Use Down Arrow ↓ in menu below to select 'View all' and press Enter)[/dim yellow]",
            )

        self._console.print(table)

    async def _prompt_review_action(
        self,
        exclusions_manager: ManageExclusionsUseCase,
        remaining_count: int,
        excluded_count: int,
    ) -> str:
        choices = [
            questionary.Choice("➕ Exclude a path or URL pattern", value="add"),
        ]

        if exclusions_manager.get_active_exclusions():
            choices.append(questionary.Choice("↩ Undo last exclusion", value="undo"))

        choices.extend(
            [
                questionary.Choice(f"👁 View all remaining URLs list ({remaining_count} total)", value="view_remaining"),
                questionary.Choice(f"📋 View all excluded URLs list ({excluded_count} total)", value="view_excluded"),
                questionary.Choice(f"🚀 Confirm and proceed to Markdown compilation ({remaining_count} pages)", value="confirm"),
                questionary.Choice("❌ Cancel crawl", value="cancel"),
            ]
        )

        answer = await questionary.select(
            "Select an action (use Arrow Keys ↑/↓ to navigate, Enter to choose):",
            choices=choices,
        ).ask_async()
        return answer if answer else "cancel"

    async def _handle_add_exclusion(
        self,
        exclusions_manager: ManageExclusionsUseCase,
        discovered_urls: List[str],
    ) -> None:
        pattern = await questionary.text(
            "Enter path, prefix, or URL pattern to exclude (e.g. /kalendarz-ogrodnika, amazon.com/bola/kula):",
            validate=lambda val: True if val.strip() else "Pattern cannot be empty",
        ).ask_async()

        if not pattern:
            return

        added = exclusions_manager.add_exclusion(pattern)
        if added:
            new_remaining = exclusions_manager.filter_urls(discovered_urls)
            self._console.print(f"\n[green bold]✔ Excluded pattern:[/] [yellow]{pattern}[/]")
            self._console.print(f"[cyan]Remaining links updated:[/] [green bold]{len(new_remaining)}[/] of {len(discovered_urls)}\n")
        else:
            self._console.print(f"\n[yellow]Pattern '{pattern}' was already active.[/yellow]\n")

    async def _handle_undo_exclusion(
        self,
        exclusions_manager: ManageExclusionsUseCase,
        discovered_urls: List[str],
    ) -> None:
        undone_pattern = exclusions_manager.undo_last_exclusion()
        if undone_pattern:
            restored_urls = exclusions_manager.filter_urls(discovered_urls)
            self._console.print(f"\n[yellow bold]↩ Undone exclusion:[/] [white]{undone_pattern}[/]")
            self._console.print(f"[cyan]Restored remaining links:[/] [green bold]{len(restored_urls)}[/] of {len(discovered_urls)}\n")

    async def _display_full_url_table(self, title: str, urls: List[str], border_color: str) -> None:
        table = Table(
            title=f"{title} ({len(urls)} items)",
            title_style=f"bold {border_color}",
            border_style=border_color,
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("#", style="dim", width=5)
        table.add_column("URL", style="white")

        for idx, url in enumerate(urls, start=1):
            table.add_row(str(idx), url)

        if not urls:
            table.add_row("-", "[dim]No URLs in this list[/dim]")

        self._console.print("\n")
        self._console.print(table)
        self._console.print("\n")
        await questionary.text("Press Enter to return to the actions menu...").ask_async()
