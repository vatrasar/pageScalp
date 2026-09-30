# PageScalp 🚀

High-speed documentation crawler & Markdown generator specifically optimized for **Google NotebookLM**.

Given any documentation or website URL (e.g. `https://amazon.com/buka`), PageScalp discovers all subpages within that exact URL prefix, lets you interactively review and exclude unwanted paths (with undo support), strips navigation/footer boilerplate, and outputs a consolidated Markdown file with an automated Table of Contents. If the text exceeds the configured character limit, it automatically splits the output into clean, sequential parts (`_part1.md`, `_part2.md`).

---

## Features

- **Strict URL Scoping**: Never escapes the seed address boundary. For `https://example.com/docs/v2/`, it will never wander into `/docs/v1/`, `/blog/`, or external domains like `empik.com`.
- **Interactive Link Review & Curation**: Displays discovered URLs before compilation. Allows excluding paths (e.g. `amazon.com/bola/kula`), viewing updated remaining URLs in real time, and undoing exclusions at any time.
- **Upfront Path Exclusions**: Define paths or patterns to exclude even before the crawler begins searching.
- **NotebookLM Optimized**: Cleans sidebars, headers, footers, and cookie banners using `trafilatura` to preserve context tokens.
- **Smart Character Limit Chunking**: Splits large documentation sets into sequential `.md` files (each with its own Table of Contents) so you never hit NotebookLM's source size ceiling.
- **Rich Terminal UI**: Live progress dashboard with spinners, metrics table, and guided interactive setup wizard.
- **Asynchronous Engine**: Fast concurrent fetching using `httpx` and `asyncio` with polite rate-limiting.

---

## Installation

Run the installation script to deploy PageScalp to your user directory (`~/.local/share/pageScalp`) and link the executable to `~/.local/bin/pagescalp`:

```bash
./install.sh
```

Ensure `~/.local/bin` is in your PATH. If not, add this line to your `~/.bashrc` or `~/.zshrc`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## Usage

### Interactive Wizard
Simply run `pagescalp` without arguments:
```bash
pagescalp
```
You will be prompted for:
1. Seed website URL
2. Upfront path exclusions (optional, e.g. `/legacy`, `/bola/kula`)
3. Maximum pages limit
4. Character limit per file (default: 1,000,000)
5. Output file destination

After discovery completes, the **Interactive Link Review Screen** lets you:
- Exclude paths or URL patterns
- View remaining and excluded URL lists
- Undo recent exclusions
- Confirm and start Markdown compilation

### Command Line Flags
You can also run directly with CLI arguments:
```bash
# Scrape documentation under /3/library with path exclusion
pagescalp "https://docs.python.org/3/library/pathlib.html" -p "/3/library" -e "/3/library/test" -m 50 -o python_docs.md

# Specify custom character limit per file (500,000 chars)
pagescalp "https://fastapi.tiangolo.com/tutorial/" -c 500000 -o fastapi_tutorial.md
```

### Options
- `url`: Seed website or documentation URL.
- `-p, --prefix`: Restrict crawling strictly to URLs starting with this path prefix.
- `-e, --exclude`: Path or URL pattern to exclude (can be repeated, e.g. `-e /legacy -e /kula`).
- `-o, --output`: Target Markdown output path.
- `-m, --max-pages`: Maximum number of pages to crawl (default: 100).
- `-c, --max-chars`: Maximum characters per file before splitting (default: 1,000,000).
- `--concurrency`: Number of concurrent workers (default: 5).
- `--delay`: Polite delay between requests in seconds (default: 0.1).
- `--no-review`: Bypass interactive review screen before compiling.
- `-i, --interactive`: Explicitly open the interactive setup wizard.

---

## Importing into NotebookLM

1. Go to [Google NotebookLM](https://notebooklm.google.com).
2. Create or open a notebook.
3. Click **Add Source** -> **Upload Sources / Markdown**.
4. Select the generated `.md` file(s).
5. All sections, headings, source URLs, and code blocks are indexed and ready for Q&A, study guides, and audio overviews!
