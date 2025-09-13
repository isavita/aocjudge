from __future__ import annotations
import os, tempfile, subprocess, json
from pathlib import Path
from typing import Tuple, Dict, Any
from langs import LANGS
from datetime import datetime

DEFAULT_TIMEOUT_S = int(os.getenv("AOCJUDGE_TIMEOUT_MS", "8000")) / 1000.0  # seconds

def _write_files(tmp: Path, code_filename: str, code: str, input_data: str, language: str):
    (tmp / "input.txt").write_text(input_data, encoding="utf-8")
    if language == "rust":
        # Create Cargo project structure
        src_dir = tmp / "src"
        src_dir.mkdir()
        (src_dir / "main.rs").write_text(code, encoding="utf-8")
        # Create Cargo.toml
        cargo_toml_content = """\
[package]
name = "aoc_solution"
version = "0.1.0"
edition = "2021"

[dependencies]
md5 = "0.7"
"""
        (tmp / "Cargo.toml").write_text(cargo_toml_content, encoding="utf-8")
    else:
        (tmp / code_filename).write_text(code, encoding="utf-8")

def _parse_docker_time(s: str) -> datetime | None:
    # Docker's timestamps are RFC3339 with nanoseconds, but Python's fromisoformat
    # before 3.11 doesn't handle 'Z' for UTC.
    if not s or s.startswith("0001-01-01"):
        return None
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    return datetime.fromisoformat(s)

def _run_container(image: str, workdir: Path, language: str) -> Tuple[int, str, str, Dict[str, Any]]:
    # Base command for docker create
    create_cmd = [
        "docker", "create",
        "--network", "none",
        "--memory", "256m",
        "--cpus", "0.5",
        "--read-only",
        "-v", f"{str(workdir)}:/app:ro",
        "-w", "/app",
    ]
    if language in {"rust", "d"}:
        create_cmd.extend(["--tmpfs", "/tmp:exec,size=64m"])

    if language == "rust":
        create_cmd.extend(["--entrypoint", "/usr/local/cargo/bin/cargo"])

    create_cmd.append(image)

    if language == "rust":
        create_cmd.extend(["run", "--release", "--quiet"])

    try:
        container_id = subprocess.check_output(create_cmd, stderr=subprocess.PIPE, text=True, encoding="utf-8").strip()
    except subprocess.CalledProcessError as e:
        return 127, "", e.stderr, {}

    rc, out, err, metrics = 1, "", "", {}
    try:
        # Start container and wait for it to finish
        start_cmd = ["docker", "start", "-a", container_id]
        proc = subprocess.run(
            start_cmd,
            input=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=DEFAULT_TIMEOUT_S,
            check=False,
        )
        rc = proc.returncode
        out = proc.stdout.decode("utf-8", "replace")
        err = proc.stderr.decode("utf-8", "replace")

    except subprocess.TimeoutExpired:
        rc, out, err = 124, "", "timeout"
        # The container might still be running, so we should stop it.
        subprocess.run(["docker", "stop", container_id], check=False, capture_output=True)

    finally:
        # Inspect container to get stats
        inspect_cmd = ["docker", "inspect", container_id]
        try:
            inspect_proc = subprocess.run(inspect_cmd, capture_output=True, check=True)
            inspect_data = json.loads(inspect_proc.stdout)[0]

            started_at = _parse_docker_time(inspect_data["State"]["StartedAt"])
            finished_at = _parse_docker_time(inspect_data["State"]["FinishedAt"])

            duration_ms = None
            if started_at and finished_at:
                duration_ms = (finished_at - started_at).total_seconds() * 1000

            metrics = {
                "duration_ms": duration_ms,
                "oom_killed": inspect_data["State"]["OOMKilled"],
                "memory_limit_bytes": inspect_data["HostConfig"]["Memory"],
            }

        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            error_message = f"\nError inspecting container: {e}"
            if not err:
                err = error_message
            else:
                err += error_message

        # Remove container
        rm_cmd = ["docker", "rm", "-f", container_id]
        subprocess.run(rm_cmd, check=False, capture_output=True)

    return rc, out, err, metrics

def run_code(language: str, code: str, input_data: str) -> Tuple[int, str, str, Dict[str, Any]]:
    cfg = LANGS.get(language)
    if not cfg:
        return 127, "", f"unsupported language: {language}", {}
    with tempfile.TemporaryDirectory(prefix=f"aocjudge-{language}-") as d:
        tmp = Path(d)
        _write_files(tmp, cfg["code_filename"], code, input_data, language)
        return _run_container(cfg["image"], tmp, language)
