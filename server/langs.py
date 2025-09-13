# server/langs.py
from __future__ import annotations

LANGS = {
    # Each language must have a Docker image and a code filename that the ENTRYPOINT expects
    "go":     {"image": "aocjudge-go", "code_filename": "main.go"},
    "python": {"image": "aocjudge-py", "code_filename": "main.py"},
}

SUPPORTED_LANGUAGES = sorted(LANGS.keys())
