from __future__ import annotations
import os, tempfile, subprocess
from pathlib import Path
from typing import Tuple

DEFAULT_TIMEOUT_S = int(os.getenv("AOCJUDGE_TIMEOUT_MS", "8000")) / 1000.0  # seconds

def _write_files(tmp: Path, code_filename: str, code: str, input_data: str):
    (tmp / code_filename).write_text(code, encoding="utf-8")
    (tmp / "input.txt").write_text(input_data, encoding="utf-8")

def _run_container(image: str, workdir: Path, stdin_data: str) -> Tuple[int, str, str]:
    cmd = [
        "docker", "run", "--rm",
        "--network", "none",
        "--memory", "256m",
        "--cpus", "0.5",
        "--read-only",
        "-v", f"{str(workdir)}:/app:ro",
        "-w", "/app",
        image
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=stdin_data.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=DEFAULT_TIMEOUT_S,
            check=False,
        )
        return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"

def run_go(code: str, input_data: str):
    with tempfile.TemporaryDirectory(prefix="aocjudge-go-") as d:
        tmp = Path(d)
        _write_files(tmp, "main.go", code, input_data)
        rc, out, err = _run_container("aocjudge-go", tmp, input_data)
        return rc, out, err

def run_python(code: str, input_data: str):
    with tempfile.TemporaryDirectory(prefix="aocjudge-py-") as d:
        tmp = Path(d)
        _write_files(tmp, "main.py", code, input_data)
        rc, out, err = _run_container("aocjudge-py", tmp, input_data)
        return rc, out, err
