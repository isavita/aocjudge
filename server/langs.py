# server/langs.py
from __future__ import annotations

LANGS = {
    # Each language must have a Docker image and a code filename that the ENTRYPOINT expects
    "rust":       {"image": "aocjudge-rs", "code_filename": "main.rs", "libs": []},
    "python":     {"image": "aocjudge-py", "code_filename": "main.py", "libs": ["numpy", "pandas"]},
    "javascript": {"image": "aocjudge-js", "code_filename": "main.js", "libs": ["lodash"]},
    "ruby":       {"image": "aocjudge-rb", "code_filename": "main.rb", "libs": ["nokogiri"]},
    "d":          {"image": "aocjudge-d",  "code_filename": "main.d", "libs": []},
}
