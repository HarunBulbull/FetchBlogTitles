# fetchBlog

A Python script that collects URLs from sitemaps, crawls pages, extracts and filters H1–H6 headings, and stores them in a MySQL database.

## What It Does

- **Sitemap parsing:** Fetches all page URLs from the configured sitemap XML endpoints.
- **Page crawling:** Visits each URL and parses the HTML.
- **Heading extraction:** Collects only text from `h1`–`h6` tags.
- **Filtering:** Keeps headings that match keywords; skips those containing domains or words from an ignore list.
- **Database:** Writes unique `(title, url)` pairs to the MySQL `headings` table.

## Requirements

- Python 3.7+
- Accessible MySQL server
- Internet connection

## Installation

```bash
# Virtual environment (optional)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Edit the following section in `main.py` for your environment:

| Variable | Description |
|----------|-------------|
| `SITEMAP_URLS` | Sitemap XML URLs to crawl |
| `KEYWORDS` | Words that must appear in a heading (e.g. `"dream"`, `"rüya"`) |
| `IGNORE_LIST` | Words that cause a heading to be skipped if present |
| `DB_CONFIG` | MySQL connection: `host`, `user`, `password`, `database` |

**Security:** Prefer using environment variables for the database password instead of hardcoding it.

## Running

```bash
python main.py
```

The script will:

1. Connect to the database and create the database and `headings` table if needed.
2. Collect URLs from all sitemaps.
3. For each URL, fetch the page, filter headings, and insert new rows into the table.
4. Close the connection when done.

## Database Table

The `headings` table structure:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT, AUTO_INCREMENT | Primary key |
| `title` | TEXT | Heading text (H1–H6) |
| `url` | VARCHAR(500) | Page URL |
| `timestamp` | TIMESTAMP | Record creation time |

Uniqueness is enforced on `title` (first 255 chars); duplicate titles are not inserted.

## Dependencies (requirements.txt)

- **requests** — HTTP requests
- **beautifulsoup4** — HTML parsing
- **lxml** — XML/HTML parser for BeautifulSoup
- **mysql-connector-python** — MySQL connector

## License

This project is shared for personal/use-at-your-own-risk purposes.
