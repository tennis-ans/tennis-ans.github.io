import os
import re

html_lines = [
    "<html>",
    "  <head>",
    "    <title>Repository for TANS Datas</title>",
    "  </head>",
    "  <body>",
    "    <h1>Repository for charted TANS Data</h1><br>",
    "    <ol>"
]

# Go through all .txt files in the current folder
for filename in sorted(os.listdir(".")):
    if filename.endswith(".txt"):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            event_match = re.search(r"\[Event:\s*(.*?)\]", content)
            url_match = re.search(r"\[Video Url:\s*(.*?)\]", content)
            event_name = event_match.group(1) if event_match else filename
            video_url = url_match.group(1) if url_match else "#"
            
            html_lines.append(f'      <li><a href="{filename}">{event_name}</a> — <a href="{video_url}">[Match Video]</a></li>')

html_lines += [
    "    </ol>",
    "  </body>",
    "</html>"
]

# Write to an output file
with open("index.html", "w", encoding="utf-8") as f:
    f.write("\n".join(html_lines))
