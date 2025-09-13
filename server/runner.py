from __future__ import annotations
import os, tempfile, subprocess
from pathlib import Path
from typing import Tuple
from langs import LANGS

DEFAULT_TIMEOUT_S = int(os.getenv("AOCJUDGE_TIMEOUT_MS", "8000")) / 1000.0  # seconds

def _write_files(tmp: Path, code_filename: str, code: str, input_data: str):
    (tmp / code_filename).write_text(code, encoding="utf-8")
    (tmp / "input.txt").write_text(input_data, encoding="utf-8")

def _run_container(image: str, workdir: Path) -> Tuple[int, str, str]:
    cmd = [
        "docker", "run", "--rm",
        "--network", "none",
        "--memory", "256m",
        "--cpus", "0.5",
        "--read-only",
        "-v", f"{str(workdir)}:/app:ro",
        "-w", "/app",
        image,  # ENTRYPOINT in the image executes the code
    ]
    try:
        # IMPORTANT: No stdin is provided. Code must read ./input.txt.
        proc = subprocess.run(
            cmd,
            input=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=DEFAULT_TIMEOUT_S,
            check=False,
        )
        return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"

def run_code(language: str, code: str, input_data: str):
    cfg = LANGS.get(language)
    if not cfg:
        return 127, "", f"unsupported language: {language}"
    with tempfile.TemporaryDirectory(prefix=f"aocjudge-{language}-") as d:
        tmp = Path(d)
        _write_files(tmp, cfg["code_filename"], code, input_data)
        rc, out, err = _run_container(cfg["image"], tmp)
        return rc, out, err
