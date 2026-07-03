"""Render docs/Project Record - Full Chronological History.md to a standalone,
self-contained HTML file.

Why this exists: the record is the project's chronological log; a rendered HTML
view (clickable TOC, tables, light/dark) is handy for reading. This is the ONLY
consumer of the `markdown` package in the venv.

Usage:  .venv\\Scripts\\python.exe -m scripts.render_record_html
Output: docs/Project Record - Full Chronological History.html  (overwritten each run)

Key detail: the in-doc Table of Contents uses GitHub-style anchors. We pass a
custom slugify so the generated heading ids match those anchors exactly (incl.
the em-dash -> double-hyphen quirk). After writing, we assert 0 broken internal
links and fail loudly if any anchor doesn't resolve.
"""
import os
import re
import sys
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_NAME = "Project Record — Full Chronological History"
SRC = os.path.join(ROOT, "docs", DOC_NAME + ".md")
OUT = os.path.join(ROOT, "docs", DOC_NAME + ".html")

# Where an anchor-jumped heading lands (vh from top). 25 = ~quarter down.
SCROLL_MARGIN_TOP = "25vh"


def gh_slugify(value, separator):
    """GitHub-compatible slug. Per-space replace (no collapsing) so the em-dash
    case keeps its double hyphen, matching the TOC anchors in the .md."""
    s = value.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = s.replace(" ", separator)
    return s


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{
    --bg: #0d1117; --fg: #c9d1d9; --muted: #8b949e; --link: #58a6ff;
    --border: #30363d; --table-alt: #161b22; --code-bg: #161b22; --accent: #1f6feb;
  }}
  @media (prefers-color-scheme: light) {{
    :root {{
      --bg: #ffffff; --fg: #1f2328; --muted: #59636e; --link: #0969da;
      --border: #d0d7de; --table-alt: #f6f8fa; --code-bg: #f6f8fa; --accent: #0969da;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    background: var(--bg); color: var(--fg); margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px; line-height: 1.6;
  }}
  .wrap {{ max-width: 980px; margin: 0 auto; padding: 32px 24px 120px; }}
  h1, h2, h3, h4 {{ font-weight: 600; line-height: 1.25; margin-top: 1.6em; margin-bottom: .5em; scroll-margin-top: {scroll}; }}
  h1 {{ font-size: 1.9em; border-bottom: 1px solid var(--border); padding-bottom: .3em; }}
  h2 {{ font-size: 1.5em; border-bottom: 1px solid var(--border); padding-bottom: .3em; }}
  h3 {{ font-size: 1.2em; }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; display: block; overflow-x: auto; }}
  th, td {{ border: 1px solid var(--border); padding: 6px 13px; }}
  tr:nth-child(2n) {{ background: var(--table-alt); }}
  th {{ background: var(--table-alt); font-weight: 600; }}
  code {{ background: var(--code-bg); padding: .2em .4em; border-radius: 6px; font-size: 85%;
         font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }}
  pre {{ background: var(--code-bg); padding: 16px; border-radius: 6px; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; }}
  blockquote {{ border-left: 4px solid var(--border); margin: 1em 0; padding: 0 1em; color: var(--muted); }}
  hr {{ border: 0; border-top: 1px solid var(--border); margin: 2em 0; }}
  .topbar {{ position: sticky; top: 0; background: var(--bg); border-bottom: 1px solid var(--border);
            padding: 10px 24px; font-size: 14px; color: var(--muted); z-index: 10; }}
  .topbar a {{ color: var(--accent); }}
</style>
</head>
<body>
<div class="topbar">{topbar}</div>
<div class="wrap">
{body}
</div>
</body>
</html>
"""


def render(src, out, title, topbar):
    """Render one markdown file to a self-contained HTML file. Shared by the
    record and daily-report renderers. Fails loudly (exit 1) on broken anchors."""
    with open(src, encoding="utf-8") as f:
        text = f.read()

    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc", "sane_lists", "nl2br"],
        extension_configs={"toc": {"slugify": gh_slugify}},
    )
    html = TEMPLATE.format(body=body, scroll=SCROLL_MARGIN_TOP, title=title, topbar=topbar)

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    # Verify every internal anchor resolves.
    hrefs = set(re.findall(r'href="#([^"]+)"', html))
    ids = set(re.findall(r'id="([^"]+)"', html))
    broken = sorted(hrefs - ids)
    print(f"Wrote {out} ({os.path.getsize(out):,} bytes)")
    print(f"internal links: {len(hrefs)}  heading ids: {len(ids)}  broken: {len(broken)}")
    for b in broken:
        print("  BROKEN ->", b)
    if broken:
        sys.exit(1)


def main():
    render(
        SRC, OUT,
        title="Project Record — Trading",
        topbar='Project Record · <a href="#table-of-contents">Jump to Table of Contents</a>',
    )


if __name__ == "__main__":
    main()
