# server/langs.py
from __future__ import annotations

LANGS = {
    # Each language must have a Docker image and a code filename that the ENTRYPOINT expects
    "rust":       {"image": "baruh/aocjudge-rs", "code_filename": "main.rs", "libs": []},
    "python":     {"image": "baruh/aocjudge-py", "code_filename": "main.py", "libs": ["numpy", "pandas"]},
    "javascript": {"image": "baruh/aocjudge-js", "code_filename": "main.js", "libs": ["lodash"]},
    "ruby":       {"image": "baruh/aocjudge-rb", "code_filename": "main.rb", "libs": ["nokogiri"]},
    "d":          {"image": "baruh/aocjudge-d",  "code_filename": "main.d", "libs": []},
    "racket":     {"image": "baruh/aocjudge-rkt", "code_filename": "main.rkt", "libs": []},
}

SUPPORTED_LANGUAGES = sorted(LANGS.keys())
