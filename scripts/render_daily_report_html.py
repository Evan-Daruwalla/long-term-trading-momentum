"""Render daily_report.md (repo root) to a standalone, self-contained HTML file.

Same treatment as the Project Record render (scripts/render_record_html.py) —
reuses its shared `render()` so the template, CSS, light/dark theme, and
GitHub-matching slugify stay identical. This is just a second entry point.

Usage:  .venv\\Scripts\\python.exe -m scripts.render_daily_report_html
Output: daily_report.html  (repo root, overwritten each run)
"""
import os

from scripts.render_record_html import render

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "daily_report.md")
OUT = os.path.join(ROOT, "daily_report.html")


def main():
    render(SRC, OUT, title="Daily Reports — Trading", topbar="Daily Reports")


if __name__ == "__main__":
    main()
