#!/usr/bin/env python3
"""Scrape HTML source for every skill page linked from the OneWave landing page."""

from __future__ import annotations

import html as html_module
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE_URL = "https://www.onewave-ai.com"
LANDING_PATH = "/resources/claude-skills"
OUTPUT_DIR = Path(__file__).parent / "scraped-pages"
USER_AGENT = "ai-scrape/1.0 (+local research)"
MAX_WORKERS = 8
RETRIES = 3


def fetch(url: str) -> str:
    last_error: Exception | None = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}") from last_error


def extract_slugs(html: str) -> list[str]:
    pattern = re.compile(r'href="/resources/claude-skills/([a-z0-9-]+)"')
    slugs = sorted(set(pattern.findall(html)))
    return slugs


def extract_skill_markdown(page_html: str) -> str | None:
    """Pull SKILL.md body rendered in the 'What it does' section."""
    match = re.search(
        r"What it does</h2>.*?<pre[^>]*>(.*?)</pre>",
        page_html,
        re.DOTALL,
    )
    if not match:
        return None
    return html_module.unescape(match.group(1).strip())


def scrape_slug(slug: str) -> tuple[str, str, bool]:
    url = f"{BASE_URL}{LANDING_PATH}/{slug}"
    html = fetch(url)

    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "page.html").write_text(html, encoding="utf-8")

    markdown = extract_skill_markdown(html)
    has_skill = False
    if markdown:
        (out_dir / "SKILL.md").write_text(markdown, encoding="utf-8")
        has_skill = True

    meta = {
        "slug": slug,
        "url": url,
        "html_bytes": len(html.encode("utf-8")),
        "has_skill_markdown": has_skill,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return slug, url, has_skill


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching landing page: {BASE_URL}{LANDING_PATH}")
    landing_html = fetch(f"{BASE_URL}{LANDING_PATH}")
    landing_dir = OUTPUT_DIR / "_landing"
    landing_dir.mkdir(parents=True, exist_ok=True)
    (landing_dir / "page.html").write_text(landing_html, encoding="utf-8")

    slugs = extract_slugs(landing_html)
    print(f"Found {len(slugs)} linked skill pages")

    manifest: dict[str, object] = {
        "source": f"{BASE_URL}{LANDING_PATH}",
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": len(slugs),
        "pages": [],
    }

    ok = 0
    missing_markdown: list[str] = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(scrape_slug, slug): slug for slug in slugs}
        for i, future in enumerate(as_completed(futures), start=1):
            slug = futures[future]
            try:
                slug, url, has_skill = future.result()
                ok += 1
                if not has_skill:
                    missing_markdown.append(slug)
                manifest["pages"].append({"slug": slug, "url": url, "has_skill_markdown": has_skill})
                print(f"[{i}/{len(slugs)}] {slug}")
            except Exception as exc:  # noqa: BLE001
                print(f"[{i}/{len(slugs)}] FAILED {slug}: {exc}", file=sys.stderr)

    manifest["success"] = ok
    manifest["missing_skill_markdown"] = missing_markdown
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"\nDone: {ok}/{len(slugs)} pages saved to {OUTPUT_DIR}")
    if missing_markdown:
        print(f"Warning: {len(missing_markdown)} pages missing extracted SKILL.md")
    return 0 if ok == len(slugs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
