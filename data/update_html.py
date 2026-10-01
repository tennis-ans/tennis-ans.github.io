"""Build a standalone index of local chartings without replacing the live library.

The public match library (index.html) loads shared files from Supabase. This
script is only for previewing .txt files stored next to it.
"""

from html import escape
from pathlib import Path
import re
from urllib.parse import quote, urlparse


data_dir = Path(__file__).resolve().parent
rows = []
for charting in sorted(data_dir.glob("*.txt")):
    content = charting.read_text(encoding="utf-8")
    event = re.search(r"\[Event:\s*(.*?)\]", content, re.IGNORECASE)
    video = re.search(r"\[Video Url:\s*(.*?)\]", content, re.IGNORECASE)
    title = escape(event.group(1) if event else charting.stem)
    filename = quote(charting.name)
    video_link = ""
    if video:
        url = video.group(1).strip()
        if urlparse(url).scheme in {"http", "https"}:
            video_link = f' — <a href="{escape(url, quote=True)}">Match video</a>'
    rows.append(f'<li><a href="{filename}">{title}</a>{video_link}</li>')

page = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Local TANS chartings</title></head>
<body><h1>Local TANS chartings</h1><p><a href="index.html">Public match library</a></p>
<ol>""" + "\n".join(rows) + """</ol></body></html>
"""
output = data_dir / "local_chartings.html"
output.write_text(page, encoding="utf-8")
print(f"Wrote {output}")
